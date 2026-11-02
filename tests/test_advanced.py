"""Real binary integrations; provider contract stubs are explicitly not model tests."""
import os,json,threading,zipfile
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from io import BytesIO
import pytest
from PIL import Image,ImageDraw,ImageFont
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from services.api.engines import run_engine,DocumentError
from services.api.advanced import readiness,cell_value

@pytest.fixture
def digital(tmp_path):
 p=tmp_path/'sample.pdf';c=canvas.Canvas(str(p));c.drawString(50,700,'PUBLIC NoirPDF SECRET-123');c.showPage();c.save();return p

@pytest.mark.parametrize('slug',['word-para-pdf','powerpoint-para-pdf','excel-para-pdf'])
def test_office_real_conversion(tmp_path,slug):
 if not readiness(slug)[0]:pytest.skip('LibreOffice not installed')
 if slug=='word-para-pdf':
  from docx import Document
  p=tmp_path/'document.docx';d=Document();d.add_heading('NoirPDF Office Test',0);d.add_table(rows=2,cols=2).cell(0,0).text='Table value';d.save(p);expected='NoirPDF Office Test'
 elif slug=='powerpoint-para-pdf':
  from pptx import Presentation
  p=tmp_path/'slides.pptx';d=Presentation()
  for text in ['NoirPDF Slide One','NoirPDF Slide Two']:d.slides.add_slide(d.slide_layouts[0]).shapes.title.text=text
  d.save(p);expected='NoirPDF Slide One'
 else:
  from openpyxl import Workbook
  p=tmp_path/'sheet.xlsx';d=Workbook();d.active.append(['NoirPDF Sheet',123]);d.active.print_area='A1:B1';d.active.column_dimensions['A'].width=30;d.save(p);expected='NoirPDF Sheet'
 result=run_engine(slug,[p],{},tmp_path/'out');pdf=PdfReader(tmp_path/'out'/result['filename']);assert expected in '\n'.join(page.extract_text() for page in pdf.pages)
 if slug=='powerpoint-para-pdf':assert len(pdf.pages)==2

@pytest.mark.parametrize('language',['por','eng','spa'])
def test_real_ocr_searchable_layer(tmp_path,language):
 if not readiness('ocr-pdf')[0]:pytest.skip('OCRmyPDF not installed')
 from services.api.advanced import command,executable
 if language not in command([executable('TESSERACT_BIN','tesseract'),'--list-langs']).splitlines():pytest.skip('OCR language not installed')
 im=Image.new('RGB',(1600,300),'white');draw=ImageDraw.Draw(im);draw.text((70,100),'DOCUMENTO CONFIDENCIAL 123456',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',58),fill='black');p=tmp_path/'scan.png';im.save(p)
 result=run_engine('ocr-pdf',[p],{'ocr_language':language},tmp_path/'out');pdf=PdfReader(tmp_path/'out'/result['filename']);assert '123456' in pdf.pages[0].extract_text();assert len(pdf.pages)==1

def test_extract_real_cells_and_formula_injection(tmp_path):
 p=tmp_path/'table.pdf';table=Table([['Produto','Valor'],['Item A','1.234,50'],['=HYPERLINK("bad")','12']]);table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,'black')]))
 SimpleDocTemplate(str(p)).build([table]);result=run_engine('pdf-para-excel',[p],{},tmp_path/'out')
 from openpyxl import load_workbook
 w=load_workbook(tmp_path/'out'/result['filename']);assert w.active['B2'].value==1234.5;assert w.active['A3'].data_type=='s';assert w.active['A3'].value.startswith('=HYPERLINK');assert w.active['B3'].value==12

def test_no_table_is_not_success(digital,tmp_path):
 with pytest.raises(DocumentError,match='Nenhuma tabela'):run_engine('pdf-para-excel',[digital],{},tmp_path/'out')

def test_redaction_removes_underlying_content_and_visual_pixels(digital,tmp_path):
 result=run_engine('ocultar-informacoes',[digital],{'text':'SECRET-123'},tmp_path/'out');p=tmp_path/'out'/result['filename'];r=PdfReader(p)
 assert r.pages[0].extract_text().strip()=='';assert not r.attachments;assert result['redactions']==1
 import pypdfium2 as pdfium
 before=pdfium.PdfDocument(str(digital));page=before[0];tp=page.get_textpage();search=tp.search('SECRET-123');start,count=search.get_next();tp.count_rects(start,count);left,bottom,right,top=tp.get_rect(0);height=page.get_height();search.close();tp.close();page.close();before.close()
 after=pdfium.PdfDocument(str(p));page=after[0];bm=page.render(scale=2);image=bm.to_pil().convert('RGB');region=image.crop((int(left*2)+2,int((height-top)*2)+2,int(right*2)-2,int((height-bottom)*2)-2));assert max(region.getextrema()[0])<35;bm.close();page.close();after.close()

def test_redaction_rejects_missing_term_and_rotations(digital,tmp_path):
 with pytest.raises(DocumentError,match='Nenhuma expressão'):run_engine('ocultar-informacoes',[digital],{'text':'ABSENT'},tmp_path/'out')
 w=PdfWriter();p=w.add_page(PdfReader(digital).pages[0]);p.rotate(90);dest=tmp_path/'rotated.pdf';w.write(dest)
 with pytest.raises(DocumentError,match='sem rotação'):run_engine('ocultar-informacoes',[dest],{'text':'SECRET'},tmp_path/'rotated-out')

def test_real_pdfa_validation(digital,tmp_path):
 if not readiness('pdf-para-pdfa')[0]:pytest.skip('veraPDF not installed')
 result=run_engine('pdf-para-pdfa',[digital],{},tmp_path/'out');assert result['conformance']=='PDF/A-2b';assert json.loads((tmp_path/'out/validation.json').read_text())['isCompliant'] is True
 assert 'PUBLIC' in PdfReader(tmp_path/'out'/result['filename']).pages[0].extract_text()

def test_noncompliant_pdfa_not_published(digital,tmp_path,monkeypatch):
 if not readiness('pdf-para-pdfa')[0]:pytest.skip('veraPDF not installed')
 import services.api.advanced as advanced
 real=advanced.command
 def validator(args,**kw):
  if args[0]==advanced.executable('VERAPDF_BIN','verapdf'):return '<report><validationReport isCompliant="false"/></report>'
  return real(args,**kw)
 monkeypatch.setattr(advanced,'command',validator)
 with pytest.raises(DocumentError,match='validação veraPDF'):run_engine('pdf-para-pdfa',[digital],{},tmp_path/'out')
 assert not (tmp_path/'out/documento-pdfa.pdf').exists()

def test_html_prints_real_text_and_blocks_network(tmp_path):
 if not readiness('html-para-pdf')[0]:pytest.skip('HTML engine not configured')
 seen=[]
 class Trap(BaseHTTPRequestHandler):
  def do_GET(self):seen.append(self.path);self.send_response(200);self.end_headers();self.wfile.write(b'UNTRUSTED')
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Trap);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  p=tmp_path/'page.html';p.write_text(f'<html><body><h1>NoirPDF HTML real</h1><script>document.body.innerHTML="SCRIPT RAN"</script><img src="http://127.0.0.1:{server.server_port}/private"><iframe src="file:///etc/passwd"></iframe></body></html>')
  result=run_engine('html-para-pdf',[p],{},tmp_path/'out');text=''.join(page.extract_text() for page in PdfReader(tmp_path/'out'/result['filename']).pages)
  assert 'NoirPDF HTML real' in text;assert 'SCRIPT RAN' not in text and 'root:' not in text;assert not seen
  with pytest.raises(DocumentError,match='URL'):run_engine('html-para-pdf',[p],{'url':'http://169.254.169.254'},tmp_path/'bad')
 finally:server.shutdown();server.server_close()

@pytest.fixture
def provider_stub(monkeypatch):
 """HTTP schema/availability test only. Does not validate a real model's quality."""
 seen=[]
 class Provider(BaseHTTPRequestHandler):
  def do_POST(self):
   payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])));seen.append((self.path,payload));self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps({'choices':[{'message':{'content':'Contract test output, not a real AI summary.'},'finish_reason':'stop'}]}).encode())
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Provider);threading.Thread(target=server.serve_forever,daemon=True).start();monkeypatch.setenv('AI_BASE_URL',f'http://127.0.0.1:{server.server_port}/v1');monkeypatch.setenv('AI_MODEL','contract-test-stub')
 yield seen
 server.shutdown();server.server_close()

@pytest.mark.parametrize('slug',['resumir-pdf','traduzir-pdf'])
def test_provider_http_contract_not_real_model(digital,tmp_path,provider_stub,slug):
 result=run_engine(slug,[digital],{'target_language':'en'},tmp_path/'out');assert 'Contract test output' in (tmp_path/'out'/result['filename']).read_text();assert provider_stub[0][0]=='/v1/chat/completions';assert provider_stub[0][1]['model']=='contract-test-stub'

def test_ai_without_configuration_is_explicit(digital,tmp_path,monkeypatch):
 monkeypatch.delenv('AI_BASE_URL',raising=False);monkeypatch.delenv('AI_MODEL',raising=False)
 with pytest.raises(DocumentError,match='Configure AI_BASE_URL'):run_engine('resumir-pdf',[digital],{},tmp_path/'out')

def test_unknown_engine_cannot_publish_a_pdf_copy(digital,tmp_path):
 with pytest.raises(DocumentError,match='Não há motor'):run_engine('unimplemented',[digital],{},tmp_path/'out')

def test_localized_cell_numbers_preserve_identifiers():
 assert cell_value('00123')=='00123';assert cell_value('1.234,56')==1234.56;assert cell_value('-12,5')==-12.5;assert cell_value('=1+1')=='=1+1'

def test_provider_url_cannot_embed_credentials(monkeypatch):
 monkeypatch.setenv('AI_BASE_URL','https://user:example-password@provider.example/v1?secret=example');monkeypatch.setenv('AI_MODEL','model')
 ready,message=readiness('resumir-pdf');assert not ready;assert 'example-password' not in message
