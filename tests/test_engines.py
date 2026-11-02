import json,zipfile
from io import BytesIO
from pathlib import Path
import pytest
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import acroform
from PIL import Image
from services.api.engines import run_engine,selection,DocumentError

@pytest.fixture
def sample(tmp_path):
    path=tmp_path/'sample.pdf'; c=canvas.Canvas(str(path))
    for n in range(1,4): c.drawString(50,700,f'Page {n} NoirPDF test'); c.showPage()
    c.save(); return path

CASES=[('juntar-pdf',{},6),('dividir-pdf',{'every':1},None),('remover-paginas',{'pages':'2'},2),('extrair-paginas',{'pages':'1,3'},2),('organizar-pdf',{'order':[3,1,2]},3),('comprimir-pdf',{},3),('reparar-pdf',{},3),('rodar-pdf',{'angle':90},3),('numeros-pagina',{},3),('marca-dagua',{'text':'CONFIDENTIAL'},3),('recortar-pdf',{'margin':24},3),('editar-pdf',{'text':'Inserted'},3),('assinar-pdf',{'text':'Maria'},3),('proteger-pdf',{'output_password':'strong-test-password'},3),('comparar-pdf',{},None),('pdf-para-jpg',{},None),('pdf-para-word',{},None),('pdf-para-powerpoint',{},None),('pdf-para-markdown',{},None)]
@pytest.mark.parametrize('slug,opts,count',CASES)
def test_engine_outputs(sample,tmp_path,slug,opts,count):
    files=[sample,sample] if slug in ('juntar-pdf','comparar-pdf') else [sample]
    result=run_engine(slug,files,opts,tmp_path/'output'); path=tmp_path/'output'/result['filename']
    assert path.exists() and path.stat().st_size>0
    if count:
        pdf=PdfReader(path)
        if pdf.is_encrypted: assert pdf.decrypt('strong-test-password')
        assert len(pdf.pages)==count
        if slug=='rodar-pdf': assert pdf.pages[0].rotation==90
        if slug=='recortar-pdf': assert pdf.pages[0].cropbox.width<pdf.pages[0].mediabox.width
        if slug in ('editar-pdf','marca-dagua','assinar-pdf'): assert opts['text'] in pdf.pages[0].extract_text()
        if slug=='organizar-pdf': assert 'Page 3' in pdf.pages[0].extract_text()
        if slug=='numeros-pagina': assert '1' in pdf.pages[0].extract_text()
    elif path.suffix=='.zip':
        with zipfile.ZipFile(path) as z:
            assert len(z.namelist())==3
            for name in z.namelist():
                if name.endswith('.pdf'): assert len(PdfReader(BytesIO(z.read(name))).pages)==1
                else:
                    with Image.open(BytesIO(z.read(name))) as image: image.verify()
    elif path.suffix=='.docx':
        from docx import Document
        assert 'Page 1' in '\n'.join(p.text for p in Document(path).paragraphs)
    elif path.suffix=='.pptx':
        from pptx import Presentation
        assert len(Presentation(path).slides)==3
    else: assert path.read_text()

@pytest.mark.parametrize('slug',['digitalizar-pdf','jpg-para-pdf'])
def test_images(tmp_path,slug):
    p=tmp_path/'image.png'; Image.new('RGB',(100,200),'red').save(p)
    result=run_engine(slug,[p],{},tmp_path/'out'); assert len(PdfReader(tmp_path/'out'/result['filename']).pages)==1

def test_unlock(sample,tmp_path):
    w=PdfWriter();w.append(PdfReader(sample));w.encrypt('known-password',algorithm='AES-256');p=tmp_path/'protected.pdf';w.write(p)
    with pytest.raises(DocumentError):run_engine('desbloquear-pdf',[p],{'password':'wrong'},tmp_path/'bad')
    result=run_engine('desbloquear-pdf',[p],{'password':'known-password'},tmp_path/'out'); assert not PdfReader(tmp_path/'out'/result['filename']).is_encrypted

def test_forms(tmp_path):
    p=tmp_path/'form.pdf';c=canvas.Canvas(str(p));c.acroForm.textfield(name='name',x=30,y=700,width=200,height=30);c.showPage();c.save()
    result=run_engine('formularios-pdf',[p],{'fields':{'name':'Maria'}},tmp_path/'out')
    assert PdfReader(tmp_path/'out'/result['filename']).get_fields()['name']['/V']=='Maria'

@pytest.mark.parametrize('value',['0','4','2-1','a','1-9','-2'])
def test_bad_range(value):
    with pytest.raises(DocumentError):selection(value,3)

def test_remove_everything(sample,tmp_path):
    with pytest.raises(DocumentError):run_engine('remover-paginas',[sample],{},tmp_path/'out')

def test_text_difference_and_multifile_rejection(sample,tmp_path):
    p=tmp_path/'different.pdf';c=canvas.Canvas(str(p));c.drawString(50,700,'Changed content');c.showPage();c.save()
    result=run_engine('comparar-pdf',[sample,p],{},tmp_path/'out')
    diff=(tmp_path/'out'/result['filename']).read_text();assert '+Changed content' in diff and '-Page 1' in diff
    with pytest.raises(DocumentError):run_engine('rodar-pdf',[sample,p],{},tmp_path/'bad')

@pytest.mark.parametrize('slug',['pdf-para-word','pdf-para-markdown','comparar-pdf'])
def test_missing_text_is_not_a_fake_conversion(tmp_path,slug):
    path=tmp_path/'scan.pdf';w=PdfWriter();w.add_blank_page(width=200,height=200);w.write(path)
    with pytest.raises(DocumentError,match='OCR'):
        run_engine(slug,[path,path] if slug=='comparar-pdf' else [path],{},tmp_path/'out')
