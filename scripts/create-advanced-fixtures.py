from pathlib import Path
from docx import Document
from pptx import Presentation
from openpyxl import Workbook
from PIL import Image,ImageDraw,ImageFont
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
p=Path('tests/fixtures');p.mkdir(exist_ok=True)
d=Document();d.add_heading('NoirPDF Word',0);t=d.add_table(rows=2,cols=2);t.cell(0,0).text='Produto';t.cell(0,1).text='Valor';t.cell(1,0).text='Item';t.cell(1,1).text='123,45';d.save(p/'word.docx')
d=Presentation()
for title in ['NoirPDF Slide 1','NoirPDF Slide 2']:d.slides.add_slide(d.slide_layouts[0]).shapes.title.text=title
d.save(p/'slides.pptx')
w=Workbook();w.active.append(['NoirPDF Excel',123]);w.active.column_dimensions['A'].width=30;w.active.print_area='A1:B1';w.save(p/'sheet.xlsx')
t=Table([['Produto','Valor'],['Item A','1.234,50'],['Item B','42']]);t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,'black')]));SimpleDocTemplate(str(p/'table.pdf')).build([t])
im=Image.new('RGB',(1600,300),'white');ImageDraw.Draw(im).text((70,100),'DOCUMENTO EXEMPLO 123456',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',58),fill='black');im.save(p/'scan.png')
(p/'page.html').write_text('<!doctype html><html lang="pt-BR"><body><h1>NoirPDF HTML</h1><p>Conversão real de HTML.</p></body></html>',encoding='utf-8')
