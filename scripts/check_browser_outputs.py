from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from pypdf import PdfReader
from PIL import Image
from docx import Document
from pptx import Presentation
base=Path('artifacts')
counts={'juntar-pdf':2,'remover-paginas':2,'extrair-paginas':1,'organizar-pdf':3,'digitalizar-pdf':1,'comprimir-pdf':3,'jpg-para-pdf':1,'rodar-pdf':3,'numeros-pagina':3,'marca-dagua':3,'recortar-pdf':3,'editar-pdf':3,'formularios-pdf':1,'assinar-pdf':3}
for slug,count in counts.items():
 r=PdfReader(base/f'browser-{slug}.pdf');assert len(r.pages)==count,slug
 if slug=='juntar-pdf':assert 'Fixture one' in r.pages[0].extract_text() and 'Fixture two' in r.pages[1].extract_text()
 if slug=='remover-paginas':assert 'Page 3' in r.pages[1].extract_text()
 if slug=='extrair-paginas':assert 'Page 2' in r.pages[0].extract_text()
 if slug=='organizar-pdf':assert 'Page 3' in r.pages[0].extract_text()
 if slug=='rodar-pdf':assert r.pages[0].rotation==90
 if slug=='recortar-pdf':assert r.pages[0].cropbox.width<r.pages[0].mediabox.width
 if slug in ('editar-pdf','marca-dagua','assinar-pdf'):assert 'NoirPDF' in r.pages[0].extract_text()
 if slug=='formularios-pdf':assert r.get_fields()['name']['/V']=='Maria'
for slug in ['dividir-pdf','pdf-para-jpg']:
 with ZipFile(base/f'browser-{slug}.zip') as z:
  assert len(z.namelist())==3
  for name in z.namelist():
   if name.endswith('.pdf'):assert len(PdfReader(BytesIO(z.read(name))).pages)==1
   else:
    with Image.open(BytesIO(z.read(name))) as im:im.verify()
assert 'Page 1' in '\n'.join(p.text for p in Document(base/'browser-pdf-para-word.docx').paragraphs)
assert len(Presentation(base/'browser-pdf-para-powerpoint.pptx').slides)==3
assert 'Fixture one' in (base/'browser-comparar-pdf.txt').read_text()
assert 'Page 1' in (base/'browser-pdf-para-markdown.md').read_text()
print('20 browser artifacts verified: PDF content/order/rotation/forms, ZIP, JPG, DOCX, PPTX and text.')
