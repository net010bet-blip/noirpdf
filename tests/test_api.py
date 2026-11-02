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

def test_reject_binary_and_csrf():
    c=client();tid=task(c)
    assert c.post(f'/api/tasks/{tid}/upload',files={'files':('evil.pdf',b'not a PDF','application/pdf')}).status_code==422
    assert c.get(f'/api/tasks/{tid}').json()['state']=='created'
    assert c.post('/api/tasks',json={'tool':'juntar-pdf'},headers={'Origin':'https://attacker.example'}).status_code==403
    assert TestClient(app).get('/api/tasks').status_code==401
    assert c.post('/api/tasks',json={'tool':'html-para-pdf'}).status_code==422

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
