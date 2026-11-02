from pathlib import Path
from zipfile import ZipFile, BadZipFile
from PIL import Image
from pypdf import PdfReader
from .engines import DocumentError

OFFICE={
 'word-para-pdf':('.docx','word/document.xml','application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
 'powerpoint-para-pdf':('.pptx','ppt/presentation.xml','application/vnd.openxmlformats-officedocument.presentationml.presentation'),
 'excel-para-pdf':('.xlsx','xl/workbook.xml','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
IMAGE_TYPES={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}
def extension(tool,name,mime):
 if tool in OFFICE:
  ext,_,allowed=OFFICE[tool]
  if Path(name).suffix.lower()!=ext or mime not in (allowed,'application/zip','application/octet-stream'):raise DocumentError(f'Selecione um arquivo {ext.upper()} válido.')
  return ext
 if tool=='html-para-pdf':
  if Path(name).suffix.lower() not in ('.html','.htm') or mime not in ('text/html','application/xhtml+xml','application/octet-stream'):raise DocumentError('Selecione um arquivo HTML em UTF-8.')
  return '.html'
 if tool in ('jpg-para-pdf','digitalizar-pdf') or (tool=='ocr-pdf' and mime in IMAGE_TYPES):
  if mime not in IMAGE_TYPES:raise DocumentError('Use JPG, PNG ou WebP.')
  return IMAGE_TYPES[mime]
 if mime not in ('application/pdf','application/octet-stream'):raise DocumentError('Selecione um PDF válido.')
 return '.pdf'

def validate(path,tool,mime):
 path=Path(path)
 with path.open('rb') as f:head=f.read(8)
 if path.suffix=='.pdf':
  if not head.startswith(b'%PDF-'):raise DocumentError('A assinatura binária do arquivo não é PDF.')
  r=PdfReader(path)
  if not r.is_encrypted and not 0<len(r.pages)<=500:raise DocumentError('Limite de 500 páginas por PDF.')
 elif path.suffix in ('.jpg','.png','.webp'):
  with Image.open(path) as image:
   if image.format not in ('JPEG','PNG','WEBP') or image.width*image.height>40_000_000:raise DocumentError('Imagem inválida ou acima de 40 megapixels.')
   image.verify()
 elif tool in OFFICE:
  try:
   with ZipFile(path) as z:
    if OFFICE[tool][1] not in z.namelist() or len(z.infolist())>10000 or sum(i.file_size for i in z.infolist())>200*1024**2:raise DocumentError('Estrutura Office inválida ou muito grande.')
  except BadZipFile:raise DocumentError('O conteúdo binário não é um arquivo Office OpenXML válido.')
 elif tool=='html-para-pdf':
  if path.stat().st_size>2*1024**2:raise DocumentError('HTML limitado a 2 MB.')
  try:text=path.read_text(encoding='utf-8-sig')
  except UnicodeError:raise DocumentError('HTML precisa usar UTF-8.')
  if not any(s in text.lower() for s in ('<html','<!doctype html','<body','<p','<h1','<div')):raise DocumentError('O arquivo não contém HTML reconhecível.')
