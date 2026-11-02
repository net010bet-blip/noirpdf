"""Local document engines. No input paths or executable names come from users."""
from pathlib import Path
from io import BytesIO
import json, zipfile, difflib
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from reportlab.pdfgen import canvas
from PIL import Image

class DocumentError(ValueError): pass

def selection(value, count):
    if not value: return list(range(count))
    result=[]
    try:
        for part in str(value).split(','):
            a,*b=part.strip().split('-')
            start=int(a); end=int(b[0]) if b else start
            if not 1 <= start <= end <= count: raise ValueError()
            result.extend(range(start-1,end))
    except (ValueError,TypeError): raise DocumentError('Intervalo inválido. Use, por exemplo, 1-3,5.')
    return list(dict.fromkeys(result))

def reader(path, password=''):
    try:
        r=PdfReader(path,strict=False)
        if r.is_encrypted and not r.decrypt(password): raise DocumentError('PDF protegido: informe a senha correta.')
        if not 0 < len(r.pages) <= 500: raise DocumentError('Limite de 500 páginas por arquivo.')
        return r
    except DocumentError: raise
    except Exception as e: raise DocumentError('Não foi possível abrir o PDF. Estrutura inválida ou arquivo corrompido.') from e

def save(writer, path):
    writer.write(path)
    # Parse the generated artifact before publishing it.
    return path

def run_engine(slug, files, options, out, progress=lambda p:None):
    out=Path(out); out.mkdir(exist_ok=True,parents=True)
    warnings=[]; artifacts=[]
    if len(files)!=1 and slug not in ('juntar-pdf','comparar-pdf','jpg-para-pdf','digitalizar-pdf'):
        raise DocumentError('Esta ferramenta processa um arquivo por tarefa nesta versão.')
    if slug in ('jpg-para-pdf','digitalizar-pdf'):
        c=canvas.Canvas(str(out/'resultado.pdf'))
        for i,f in enumerate(files):
            with Image.open(f) as im:
                im.load()
                w,h=im.size
                size=(595.28,841.89) if options.get('paper','A4')=='A4' else (float(w),float(h))
                if options.get('landscape'): size=tuple(reversed(sorted(size)))
                c.setPageSize(size); margin=float(options.get('margin',24)); scale=min((size[0]-2*margin)/w,(size[1]-2*margin)/h)
                if scale<=0: raise DocumentError('Margem maior que a página.')
                from reportlab.lib.utils import ImageReader
                c.drawImage(ImageReader(im.convert('RGB')),(size[0]-w*scale)/2,(size[1]-h*scale)/2,w*scale,h*scale)
                c.showPage(); progress(10+int(75*(i+1)/len(files)))
        c.save(); artifacts=[out/'resultado.pdf']
    else:
        readers=[reader(f,options.get('password','')) for f in files]; r=readers[0]; count=len(r.pages)
        selected=selection(options.get('pages',''),count); w=PdfWriter()
        if slug=='juntar-pdf':
            for rr in readers: w.append(rr)
        elif slug in ('extrair-paginas','remover-paginas','organizar-pdf','dividir-pdf'):
            if slug=='remover-paginas': selected=[i for i in range(count) if i not in selected]
            if not selected: raise DocumentError('O resultado precisa conter pelo menos uma página.')
            if slug=='organizar-pdf' and options.get('order'):
                selected=[int(i)-1 for i in options['order']]
                if not selected or any(i<0 or i>=count for i in selected): raise DocumentError('Ordem de páginas inválida.')
            if slug=='dividir-pdf':
                step=int(options.get('every',1))
                if not 1<=step<=count: raise DocumentError('Quantidade de páginas por arquivo inválida.')
                for j in range(0,len(selected),step):
                    part=PdfWriter()
                    for k in selected[j:j+step]: part.add_page(r.pages[k])
                    artifacts.append(save(part,out/f'parte-{j//step+1}.pdf'))
            else:
                for i in selected: w.add_page(r.pages[i])
        elif slug=='pdf-para-markdown':
            if not any(p.extract_text() for p in r.pages): raise DocumentError('Nenhum texto extraível. Este PDF requer OCR, ainda indisponível nesta versão.')
            (out/'documento.md').write_text('\n\n'.join(f'<!-- Página {i+1} -->\n\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)),encoding='utf-8')
            warnings.append('Extração de texto em ordem de leitura do motor; sem OCR ou reconstrução de tabelas e imagens.')
            artifacts=[out/'documento.md']
        elif slug=='pdf-para-word':
            if not any(p.extract_text() for p in r.pages): raise DocumentError('Nenhum texto extraível. Este PDF requer OCR, ainda indisponível nesta versão.')
            from docx import Document
            doc=Document()
            for i,p in enumerate(r.pages):
                if i: doc.add_page_break()
                for line in (p.extract_text() or '').splitlines(): doc.add_paragraph(line)
            doc.save(out/'documento.docx'); artifacts=[out/'documento.docx']
            warnings.append('DOCX com texto editável. Tabelas, imagens e diagramação não são reconstruídas. Sem OCR.')
        elif slug in ('pdf-para-jpg','pdf-para-powerpoint'):
            import pypdfium2 as pdfium
            pdf=pdfium.PdfDocument(str(files[0]),password=options.get('password') or None)
            for i in selected:
                page=pdf[i]; bitmap=page.render(scale=2 if options.get('quality')=='high' else 1.2)
                im=bitmap.to_pil(); dest=out/f'pagina-{i+1}.jpg'; im.save(dest,quality=90); artifacts.append(dest)
                im.close(); bitmap.close(); page.close(); progress(10+int(70*(i+1)/count))
            pdf.close()
            if slug=='pdf-para-powerpoint':
                from pptx import Presentation
                from pptx.util import Inches
                deck=Presentation(); deck.slide_width=Inches(8.27); deck.slide_height=Inches(11.69)
                for f in artifacts:
                    slide=deck.slides.add_slide(deck.slide_layouts[6]); slide.shapes.add_picture(str(f),0,0,width=deck.slide_width,height=deck.slide_height)
                deck.save(out/'apresentacao.pptx'); artifacts=[out/'apresentacao.pptx']; warnings.append('Modo visual: páginas como imagens; conteúdo dos slides não editável. Páginas ajustadas a A4.')
        elif slug=='comparar-pdf':
            if len(readers)!=2: raise DocumentError('Selecione exatamente dois PDFs.')
            a=[p.extract_text() or '' for p in r.pages]; b=[p.extract_text() or '' for p in readers[1].pages]
            if not any(a) or not any(b): raise DocumentError('Comparação textual exige texto extraível nos dois documentos. OCR ainda indisponível.')
            diff='\n'.join(difflib.unified_diff('\n'.join(a).splitlines(),'\n'.join(b).splitlines(),fromfile='original',tofile='comparado',lineterm=''))
            (out/'comparacao.txt').write_text(diff or 'Nenhuma diferença textual encontrada.',encoding='utf-8'); artifacts=[out/'comparacao.txt']; warnings.append('Comparação textual; diferenças visuais e documentos escaneados não são avaliados.')
        else:
            for i,source_page in enumerate(r.pages):
                p=w.add_page(source_page)
                if slug=='rodar-pdf' and i in selected:
                    angle=int(options.get('angle',90))
                    if angle not in (90,180,270): raise DocumentError('Ângulo inválido.')
                    p.rotate(angle)
                if slug=='recortar-pdf' and i in selected:
                    margin=float(options.get('margin',24)); box=p.mediabox
                    if margin<0 or 2*margin>=min(float(box.width),float(box.height)): raise DocumentError('Margem de recorte inválida.')
                    p.cropbox=RectangleObject([float(box.left)+margin,float(box.bottom)+margin,float(box.right)-margin,float(box.top)-margin])
                if slug in ('numeros-pagina','marca-dagua','editar-pdf','assinar-pdf') and i in selected:
                    buf=BytesIO(); pw,ph=float(p.mediabox.width),float(p.mediabox.height); c=canvas.Canvas(buf,pagesize=(pw,ph))
                    text=str(options.get('text','NoirPDF'))[:1000]; fs=float(options.get('font_size',20))
                    if not 6<=fs<=144: raise DocumentError('Tamanho da fonte deve estar entre 6 e 144.')
                    c.setFont('Helvetica',fs)
                    if slug=='numeros-pagina': c.drawCentredString(pw/2,24,str(i+int(options.get('start',1))))
                    elif slug=='marca-dagua':
                        c.setFillAlpha(0.25); c.translate(pw/2,ph/2); c.rotate(45); c.drawCentredString(0,0,text)
                    else: c.drawString(float(options.get('x',50)),float(options.get('y',80)),text)
                    c.save(); buf.seek(0); p.merge_page(PdfReader(buf).pages[0])
                progress(10+int(65*(i+1)/count))
            if slug=='formularios-pdf':
                w=PdfWriter(); w.append(r)
                values=options.get('fields',{})
                if not isinstance(values,dict) or not r.get_fields(): raise DocumentError('O PDF não contém campos AcroForm, ou os valores são inválidos.')
                for p in w.pages: w.update_page_form_field_values(p,values,auto_regenerate=False)
            if slug=='comprimir-pdf':
                for p in w.pages: p.compress_content_streams(level=9)
                w.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
                warnings.append('Otimização sem perda de streams e objetos. Imagens não são reamostradas; o tamanho pode não diminuir.')
            if slug=='reparar-pdf': warnings.append('Documento relido e reescrito. Não há garantia de recuperação de conteúdo perdido ou de reparo de todo dano.')
            if slug=='proteger-pdf':
                password=str(options.get('output_password',''))
                if len(password)<8: raise DocumentError('Use uma senha com pelo menos 8 caracteres.')
                w.encrypt(password,algorithm='AES-256')
            if slug=='recortar-pdf': warnings.append('Recorte visual: o conteúdo fora da área continua no arquivo. Não use como redação de dados.')
            if slug=='assinar-pdf': warnings.append('Assinatura visual digitada, sem certificado, comprovação de identidade ou assinatura criptográfica.')
            if slug=='editar-pdf': warnings.append('Inserção de texto: não altera nem remove texto existente. Coordenadas em pontos a partir do canto inferior esquerdo.')
        if not artifacts: artifacts=[save(w,out/'resultado.pdf')]
    for f in artifacts:
        if f.suffix=='.pdf':
            check=reader(f,options.get('output_password','')); assert len(check.pages)>0
    if len(artifacts)>1:
        with zipfile.ZipFile(out/'resultados.zip','w',zipfile.ZIP_DEFLATED) as z:
            for f in artifacts: z.write(f,f.name)
        result=out/'resultados.zip'
    else: result=artifacts[0]
    original=sum(Path(f).stat().st_size for f in files)
    if slug=='comprimir-pdf' and result.stat().st_size>=original:
        warnings.append('O arquivo não ficou menor com esta otimização. O original pode já estar otimizado.')
    return {'filename':result.name,'bytes':result.stat().st_size,'original_bytes':original,'warnings':warnings}
