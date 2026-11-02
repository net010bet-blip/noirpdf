import os, json, uuid, hashlib, secrets, shutil, time, subprocess, sys, asyncio, signal, threading
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict,deque
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, Text, Float, text as sql_text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import declarative_base, sessionmaker
from PIL import Image
from .engines import reader, DocumentError
from .uploads import extension,validate
from .advanced import readiness

ROOT=Path(__file__).resolve().parents[2]
DATA=Path(os.getenv('DATA_DIR',ROOT/'data')).resolve(); DATA.mkdir(parents=True,exist_ok=True)
CATALOG=json.loads((ROOT/'packages/shared/catalog.json').read_text())
DATABASE=os.getenv('DATABASE_URL',f'sqlite:///{DATA}/noirpdf.db')
engine=create_engine(DATABASE,connect_args={'check_same_thread':False} if DATABASE.startswith('sqlite') else {})
Session=sessionmaker(engine); Base=declarative_base()
TTL=int(os.getenv('FILE_TTL_SECONDS','3600')); MAX_BYTES=50*1024*1024
class Task(Base):
    __tablename__='tasks'
    id=Column(String,primary_key=True); owner=Column(String,index=True); tool=Column(String)
    state=Column(String,default='created'); progress=Column(Integer,default=0)
    files=Column(Text,default='[]'); result=Column(Text,nullable=True); error=Column(Text,nullable=True)
    created=Column(Float,default=time.time); expires=Column(Float)
Base.metadata.create_all(engine)
def expire_files():
    with Session() as db:
        for t in db.query(Task).filter(Task.expires<time.time(),Task.state!='expired'):
            shutil.rmtree(DATA/t.id,ignore_errors=True); t.state='expired'; t.files='[]'; t.result=None
        db.commit()

@asynccontextmanager
async def lifespan(app):
    if os.getenv('EXECUTOR','local')!='celery':
        with Session() as db:
            for t in db.query(Task).filter(Task.state.in_(['queued','processing','uploading'])):
                t.state='failed';t.error='Operação interrompida pela reinicialização do serviço. Envie o arquivo novamente.'
            db.commit()
    async def sweep():
        while True:
            try:await asyncio.to_thread(expire_files)
            except (SQLAlchemyError,OSError):pass
            await asyncio.sleep(60)
    timer=asyncio.create_task(sweep())
    yield
    timer.cancel()
    try: await timer
    except asyncio.CancelledError: pass

app=FastAPI(title='NoirPDF API',version='0.1.0',lifespan=lifespan)
pool=ThreadPoolExecutor(max_workers=int(os.getenv('MAX_CONCURRENT_TASKS','2'))); limits=defaultdict(deque)

def owner(request):
    token=request.cookies.get('noir_session')
    if not token: raise HTTPException(401,'Sessão necessária. Atualize a página.')
    return hashlib.sha256(token.encode()).hexdigest()

def load(db, tid, request):
    t=db.get(Task,tid)
    if not t or t.owner!=owner(request): raise HTTPException(404,'Tarefa não encontrada.')
    if time.time()>t.expires:
        shutil.rmtree(DATA/t.id,ignore_errors=True); t.state='expired'; db.commit()
        raise HTTPException(410,'Os arquivos desta tarefa expiraram.')
    return t

def public(t):
    return dict(id=t.id,tool=t.tool,state=t.state,progress=t.progress,files=json.loads(t.files),result=json.loads(t.result) if t.result else None,error=t.error,expires=t.expires)

@app.exception_handler(SQLAlchemyError)
async def database_unavailable(request,error):
    return JSONResponse(status_code=503,content={'detail':'Banco de tarefas indisponível. Aguarde a recuperação do serviço e tente novamente.'})

@app.middleware('http')
async def guard(request,call_next):
    if request.method in ('POST','DELETE','PUT'):
        if int(request.headers.get('content-length','0'))>100*1024*1024:
            return Response('Limite de 100 MB por requisição.',status_code=413)
        origin=request.headers.get('origin')
        allowed=os.getenv('PUBLIC_ORIGIN','http://localhost:3000')
        if origin and origin!=allowed: return Response('Origem não permitida',status_code=403)
        key=hashlib.sha256((request.cookies.get('noir_session') or (request.client.host if request.client else '')).encode()).hexdigest()
        q=limits[key]; now=time.time()
        while q and q[0]<now-60: q.popleft()
        if len(q)>=60: return Response('Limite de requisições. Tente em um minuto.',status_code=429)
        q.append(now)
        if len(limits)>10000:
            for k in list(limits):
                if not limits[k] or limits[k][-1]<now-60: del limits[k]
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/api/session')
def session(request:Request,response:Response):
    if not request.cookies.get('noir_session'):
        response.set_cookie('noir_session',secrets.token_urlsafe(32),httponly=True,samesite='strict',secure=os.getenv('COOKIE_SECURE')=='true',max_age=86400*30)
    return {'mode':'anonymous','retention_seconds':TTL}

@app.get('/api/tools')
def tools():
    return [{**t,'ready':readiness(t['slug'])[0],'reason':readiness(t['slug'])[1]} for t in CATALOG]

@app.get('/api/health')
def health():
    with Session() as db:db.execute(sql_text('SELECT 1'))
    probe=DATA/'.health-check'
    try:probe.write_bytes(b'ok');probe.unlink(missing_ok=True)
    except OSError:raise HTTPException(503,'Armazenamento temporário indisponível.')
    return {'status':'ok','executor':os.getenv('EXECUTOR','local'),'storage':'ready'}

class Create(BaseModel): tool:str
class Execute(BaseModel): options:dict=Field(default_factory=dict)
@app.post('/api/tasks',status_code=201)
def create(body:Create,request:Request):
    tool=next((t for t in CATALOG if t['slug']==body.tool),None)
    if not tool or not tool['available']: raise HTTPException(422,'Motor indisponível nesta versão. Consulte as limitações.')
    ready,reason=readiness(body.tool)
    if not ready: raise HTTPException(503,reason)
    with Session() as db:
        active=db.query(Task).filter(Task.owner==owner(request),Task.expires>time.time()).count()
        if active>=30: raise HTTPException(429,'Limite de 30 tarefas ativas. Exclua tarefas anteriores.')
        t=Task(id=str(uuid.uuid4()),owner=owner(request),tool=body.tool,expires=time.time()+TTL); db.add(t); db.commit(); db.refresh(t)
        (DATA/t.id/'input').mkdir(parents=True); return public(t)

validation_slots=threading.BoundedSemaphore(2)
def validate_isolated(path,tool,mime):
    with validation_slots:
        try:
            check=subprocess.run([sys.executable,'-m','services.worker.validate',str(path),tool,mime or ''],capture_output=True,text=True,timeout=12)
        except subprocess.TimeoutExpired:raise DocumentError('O arquivo excedeu o tempo de validação. Tente um documento menor ou recuperado.')
        except OSError:raise DocumentError('Serviço de validação indisponível. Confira a instalação do servidor.')
        if check.returncode:
            try:message=json.loads(check.stdout).get('error','Arquivo inválido ou acima do limite de validação.')
            except (ValueError,TypeError):message='Arquivo inválido ou acima do limite de validação.'
            raise DocumentError(message)

@app.post('/api/tasks/{tid}/upload')
async def upload(tid:str,request:Request,files:list[UploadFile]=File(...)):
    with Session() as db:
        t=load(db,tid,request)
        if t.state not in ('created','ready'): raise HTTPException(409,'Tarefa não aceita arquivos neste estado.')
        existing=json.loads(t.files)
        if not 1<=len(files)+len(existing)<=20: raise HTTPException(422,'Selecione de 1 a 20 arquivos.')
        added=[]; t.state='uploading'; db.commit()
        try:
            for f in files:
                ext=extension(t.tool,f.filename or '',f.content_type)
                key=uuid.uuid4().hex+ext; path=DATA/t.id/'input'/key
                size=0
                added.append({'key':key,'name':Path((f.filename or 'arquivo').replace('\\','/')).name[:120],'bytes':0})
                with path.open('wb') as target:
                    while chunk:=await f.read(1024*1024):
                        size+=len(chunk)
                        if size>MAX_BYTES: raise DocumentError('Limite de 50 MB por arquivo.')
                        target.write(chunk)
                added[-1]['bytes']=size
                await asyncio.to_thread(validate_isolated,path,t.tool,f.content_type)
            t.files=json.dumps(existing+added); t.state='ready'; db.commit(); return public(t)
        except Exception as e:
            for item in added: (DATA/t.id/'input'/item['key']).unlink(missing_ok=True)
            t.state='ready' if existing else 'created'; db.commit()
            raise HTTPException(422,str(e) if isinstance(e,DocumentError) else 'Arquivo inválido ou não suportado.')

@app.get('/api/tasks')
def history(request:Request):
    with Session() as db:
        return [public(t) for t in db.query(Task).filter(Task.owner==owner(request),Task.expires>time.time()).order_by(Task.created.desc()).limit(50)]

@app.get('/api/tasks/{tid}')
def status(tid:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        result=public(t)
        progress_file=DATA/t.id/'progress'
        if t.state=='processing' and progress_file.exists():
            try: result['progress']=int(progress_file.read_text())
            except ValueError: pass
        return result

@app.get('/api/tasks/{tid}/input/{key}')
def input_file(tid:str,key:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        if key not in [f['key'] for f in json.loads(t.files)]: raise HTTPException(404)
        return FileResponse(DATA/t.id/'input'/key,media_type='application/pdf')

@app.post('/api/tasks/{tid}/execute',status_code=202)
def execute(tid:str,body:Execute,request:Request):
    if len(json.dumps(body.options))>20000: raise HTTPException(422,'Configuração muito grande.')
    with Session() as db:
        t=load(db,tid,request)
        if t.state!='ready': raise HTTPException(409,'Envie arquivos antes de executar.')
        (DATA/t.id/'manifest.json').write_text(json.dumps([f['key'] for f in json.loads(t.files)]))
        t.state='queued'; t.progress=0; db.commit()
        if os.getenv('EXECUTOR')=='celery':
            from services.worker.tasks import process
            try: process.delay(tid,body.options)
            except Exception:
                t.state='failed'; t.error='Fila indisponível. Tente novamente quando o serviço voltar.'; db.commit()
                raise HTTPException(503,t.error)
        else: pool.submit(process_task,tid,body.options)
        return public(t)

def process_task(tid,options):
    with Session() as db:
        t=db.get(Task,tid)
        if not t or t.state!='queued': return
        t.state='processing'; t.progress=5; db.commit()
        try:
            command=[sys.executable,'-m','services.worker.runner',str(DATA/t.id),t.tool]
            proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
            try: stdout,_=proc.communicate(json.dumps(options),timeout=180)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL); proc.communicate(); raise DocumentError('Tempo limite de processamento excedido.')
            if proc.returncode!=0:
                try: message=json.loads(stdout).get('error','Falha no processamento.')
                except Exception: message='Falha no processamento. Documento inválido ou limite de recursos.'
                raise DocumentError(message)
            result=json.loads(stdout)
            db.refresh(t)
            if t.state!='processing': shutil.rmtree(DATA/t.id/'output',ignore_errors=True); return
            t.result=json.dumps(result); t.state='completed'; t.progress=100
        except Exception as e:
            db.refresh(t)
            if t.state!='cancelled': t.state='failed'; t.error=str(e) if isinstance(e,DocumentError) else 'Falha interna no processamento.'
        db.commit()

@app.get('/api/tasks/{tid}/download')
def download(tid:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        if t.state!='completed': raise HTTPException(409,'Resultado não disponível.')
        filename=json.loads(t.result)['filename']; return FileResponse(DATA/t.id/'output'/filename,filename=filename)

@app.get('/api/tasks/{tid}/text')
def preview_text(tid:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        if t.state!='completed':raise HTTPException(409,'Resultado não disponível.')
        name=json.loads(t.result).get('text_preview')
        if name not in ('resumo.txt','traducao.txt'):raise HTTPException(404)
        return {'text':(DATA/t.id/'output'/name).read_text(encoding='utf-8')}

@app.get('/api/tasks/{tid}/validation')
def validation(tid:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        if t.state!='completed' or not json.loads(t.result).get('validation_report'):raise HTTPException(404)
        return FileResponse(DATA/t.id/'output'/'validation.json',filename='validacao-pdfa.json')

@app.post('/api/tasks/{tid}/cancel')
def cancel(tid:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        if t.state not in ('queued','created','ready'): raise HTTPException(409,'Cancelamento disponível antes do processamento.')
        t.state='cancelled'; db.commit(); return public(t)

@app.delete('/api/tasks/{tid}',status_code=204)
def delete(tid:str,request:Request):
    with Session() as db:
        t=load(db,tid,request)
        if t.state in ('processing','uploading'): raise HTTPException(409,'Aguarde o processamento para excluir.')
        shutil.rmtree(DATA/t.id,ignore_errors=True); db.delete(t); db.commit()
