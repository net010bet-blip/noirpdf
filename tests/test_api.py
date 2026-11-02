import os,time
from io import BytesIO
os.environ['DATA_DIR']='/tmp/noirpdf-api-tests'
from fastapi.testclient import TestClient
from services.api.main import app
from pypdf import PdfReader
from reportlab.pdfgen import canvas

def pdf_bytes(text='API test'):
    b=BytesIO();c=canvas.Canvas(b);c.drawString(40,700,text);c.showPage();c.save();return b.getvalue()

def client():
    c=TestClient(app);assert c.get('/api/session').status_code==200;return c

def task(c,tool='juntar-pdf'):
    r=c.post('/api/tasks',json={'tool':tool});assert r.status_code==201;return r.json()['id']

def test_full_merge_access_and_delete():
    c=client();tid=task(c)
    r=c.post(f'/api/tasks/{tid}/upload',files=[('files',('a.pdf',pdf_bytes('First'),'application/pdf')),('files',('b.pdf',pdf_bytes('Second'),'application/pdf'))]);assert r.status_code==200
    other=client()
    for suffix in ('','/download','/input/'+r.json()['files'][0]['key']):assert other.get(f'/api/tasks/{tid}'+suffix).status_code==404
    assert c.post(f'/api/tasks/{tid}/execute',json={'options':{}}).status_code==202
    for _ in range(100):
        state=c.get(f'/api/tasks/{tid}').json()
        if state['state'] in ('completed','failed'):break
        time.sleep(.1)
    assert state['state']=='completed',state
    r=c.get(f'/api/tasks/{tid}/download');assert r.status_code==200
    result=PdfReader(BytesIO(r.content));assert len(result.pages)==2;assert 'First' in result.pages[0].extract_text();assert 'Second' in result.pages[1].extract_text()
    assert c.delete(f'/api/tasks/{tid}').status_code==204
    assert c.get(f'/api/tasks/{tid}').status_code==404

def test_reject_binary_and_csrf(monkeypatch):
    monkeypatch.delenv('AI_BASE_URL',raising=False)
    monkeypatch.delenv('AI_MODEL',raising=False)
    c=client();tid=task(c)
    assert c.post(f'/api/tasks/{tid}/upload',files={'files':('evil.pdf',b'not a PDF','application/pdf')}).status_code==422
    assert c.get(f'/api/tasks/{tid}').json()['state']=='created'
    assert c.post('/api/tasks',json={'tool':'juntar-pdf'},headers={'Origin':'https://attacker.example'}).status_code==403
    assert TestClient(app).get('/api/tasks').status_code==401
    assert c.post('/api/tasks',json={'tool':'resumir-pdf'}).status_code==503

def test_cancel_and_download_state():
    c=client();tid=task(c)
    assert c.get(f'/api/tasks/{tid}/download').status_code==409
    assert c.post(f'/api/tasks/{tid}/cancel').json()['state']=='cancelled'
    assert c.post(f'/api/tasks/{tid}/execute',json={'options':{}}).status_code==409

def test_expiry_and_cleanup():
    from services.api.main import Session,Task,DATA,expire_files
    c=client();tid=task(c)
    assert c.post(f'/api/tasks/{tid}/upload',files={'files':('safe.pdf',pdf_bytes(),'application/pdf')}).status_code==200
    with Session() as db:
        t=db.get(Task,tid);t.expires=time.time()-1;db.commit()
    expire_files()
    assert not (DATA/tid).exists()
    assert c.get(f'/api/tasks/{tid}').status_code==410

def test_path_names_do_not_escape_and_duplicate_execute():
    from services.api.main import DATA
    c=client();tid=task(c)
    r=c.post(f'/api/tasks/{tid}/upload',files={'files':('../../outside.pdf',pdf_bytes(),'application/pdf')})
    assert r.status_code==200
    info=r.json()['files'][0];assert info['name']=='outside.pdf';assert '/' not in info['key']
    assert (DATA/tid/'input'/info['key']).is_file()
    assert c.post(f'/api/tasks/{tid}/execute',json={'options':{}}).status_code==202
    assert c.post(f'/api/tasks/{tid}/execute',json={'options':{}}).status_code==409

def test_queue_failure_is_not_stuck_and_health(monkeypatch):
    import services.worker.tasks as worker
    monkeypatch.setenv('EXECUTOR','celery')
    def unavailable(*_args,**_kwargs):raise RuntimeError('broker offline')
    monkeypatch.setattr(worker.process,'delay',unavailable)
    c=client();assert c.get('/api/health').json()['status']=='ok';tid=task(c)
    assert c.post(f'/api/tasks/{tid}/upload',files={'files':('safe.pdf',pdf_bytes(),'application/pdf')}).status_code==200
    r=c.post(f'/api/tasks/{tid}/execute',json={'options':{}});assert r.status_code==503
    assert c.get(f'/api/tasks/{tid}').json()['state']=='failed'
    other=client()
    for route in ['text','validation']:assert other.get(f'/api/tasks/{tid}/{route}').status_code==404

def test_office_signature_rejects_renamed_pdf(monkeypatch):
    import services.api.main as main
    actual=main.readiness
    monkeypatch.setattr(main,'readiness',lambda slug:(True,None) if slug=='word-para-pdf' else actual(slug))
    c=client();tid=task(c,'word-para-pdf')
    r=c.post(f'/api/tasks/{tid}/upload',files={'files':('renamed.docx',pdf_bytes(),'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
    assert r.status_code==422;assert c.get(f'/api/tasks/{tid}').json()['state']=='created'

def test_database_outage_returns_actionable_503_without_details(monkeypatch):
    import services.api.main as main
    from sqlalchemy.exc import SQLAlchemyError
    c=client()
    class Broken:
        def __enter__(self):raise SQLAlchemyError('private connection detail')
        def __exit__(self,*args):pass
    monkeypatch.setattr(main,'Session',Broken)
    response=c.get('/api/health');assert response.status_code==503;assert 'Banco de tarefas indisponível' in response.json()['detail'];assert 'private connection detail' not in response.text
