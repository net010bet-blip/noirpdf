"""Same-origin Next + FastAPI supervised in a single free-tier web service."""
import os,subprocess,sys,signal,time,http.client
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
children=[]
def stop(*_):
    for child in children:
        if child.poll() is None: child.terminate()
    for child in children:
        try: child.wait(timeout=8)
        except subprocess.TimeoutExpired: child.kill()
    sys.exit(0)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
env=os.environ.copy()
if not env.get('PUBLIC_ORIGIN') and env.get('RENDER_EXTERNAL_URL'):env['PUBLIC_ORIGIN']=env['RENDER_EXTERNAL_URL'].rstrip('/')
# Refuse to expose an unhealthy document service silently.
check=subprocess.run([sys.executable,'-m','services.api.doctor','--strict'],cwd=ROOT,env=env,capture_output=True,text=True)
if check.returncode:
    print('Configuração incompleta dos motores. Execute python -m services.api.doctor para verificar.',file=sys.stderr);sys.exit(1)
children.append(subprocess.Popen([sys.executable,'-m','uvicorn','services.api.main:app','--host','127.0.0.1','--port','8000','--no-access-log'],cwd=ROOT,env=env))
# Do not serve the frontend until the document API answers on the local socket.
for attempt in range(60):
    if children[0].poll() is not None:
        print('A API não iniciou. Verifique os logs e a configuração.',file=sys.stderr);stop()
    try:
        conn=http.client.HTTPConnection('127.0.0.1',8000,timeout=2)
        conn.request('GET','/api/health');healthy=conn.getresponse().status==200;conn.close()
        if healthy:break
    except OSError:pass
    time.sleep(.5)
else:
    print('A API não ficou saudável dentro do prazo.',file=sys.stderr);stop()
children.append(subprocess.Popen(['node',str(ROOT/'node_modules/next/dist/bin/next'),'start','--hostname','0.0.0.0','--port',env.get('PORT','10000')],cwd=ROOT/'apps/web',env=env))
while True:
    for child in children:
        if child.poll() is not None:
            code=child.returncode
            for other in children:
                if other.poll() is None:other.terminate()
            sys.exit(code or 1)
    time.sleep(.5)
