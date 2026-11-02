import {PDFDocument,StandardFonts,degrees,PDFTextField,PDFCheckBox,PDFDropdown,PDFRadioGroup} from 'pdf-lib';
import JSZip from 'jszip';
import {basePath} from './browser-mode';
type Options=Record<string,any>;
export function selection(value:string|undefined,count:number):number[]{
 if(!value)return Array.from({length:count},(_,i)=>i);
 const result=new Set<number>();
 for(const part of value.split(',')){if(!/^\d+(?:-\d+)?$/.test(part.trim()))throw Error('Intervalo inválido. Use 1-3,5.');const [a,end]=part.trim().split('-').map(Number);const b=end??a;if(a<1||a>b||b>count)throw Error('Intervalo fora dos limites do documento.');for(let n=a;n<=b;n++)result.add(n-1);}
 return [...result];
}
function blob(bytes:Uint8Array,type='application/pdf'){return new Blob([bytes as BlobPart],{type});}
async function pdfjs(file:File,password?:string){const lib=await import('pdfjs-dist');lib.GlobalWorkerOptions.workerSrc=`${basePath}/pdf.worker.min.mjs`;return lib.getDocument({data:new Uint8Array(await file.arrayBuffer()),password}).promise;}
async function load(file:File){try{const doc=await PDFDocument.load(await file.arrayBuffer(),{updateMetadata:false});if(doc.getPageCount()>500||doc.getPageCount()<1)throw Error();return doc;}catch{throw Error('PDF inválido, protegido ou acima de 500 páginas. PDFs protegidos precisam da versão com servidor.');}}
async function image(file:File){const bitmap=await createImageBitmap(file);if(bitmap.width*bitmap.height>40_000_000){bitmap.close();throw Error('Imagem excede 40 megapixels.');}const canvas=document.createElement('canvas');canvas.width=bitmap.width;canvas.height=bitmap.height;canvas.getContext('2d')!.drawImage(bitmap,0,0);bitmap.close();return new Uint8Array(await(await new Promise<Blob>((res,rej)=>canvas.toBlob(b=>b?res(b):rej(Error('Imagem inválida.')),'image/png'))).arrayBuffer());}
export async function runBrowserEngine(slug:string,files:File[],o:Options,progress:(n:number)=>Promise<void>){
 if(files.length!==1&&!['juntar-pdf','comparar-pdf','jpg-para-pdf','digitalizar-pdf'].includes(slug))throw Error('Selecione um arquivo por tarefa nesta ferramenta.');
 if(slug==='comparar-pdf'&&files.length!==2)throw Error('Selecione exatamente dois PDFs.');
 let artifacts:{name:string;blob:Blob}[]=[];const warnings:string[]=[];await progress(5);
 const pdfOutput=async(doc:PDFDocument,name='resultado.pdf')=>{const data=await doc.save({useObjectStreams:true});const check=await PDFDocument.load(data);if(!check.getPageCount())throw Error('O resultado não contém páginas.');artifacts.push({name,blob:blob(data)});};
 if(['jpg-para-pdf','digitalizar-pdf'].includes(slug)){
  const out=await PDFDocument.create();const margin=Number(o.margin??24);if(!Number.isFinite(margin)||margin<0||margin>=297)throw Error('Margem inválida.');
  for(let i=0;i<files.length;i++){const im=await out.embedPng(await image(files[i]));const page=out.addPage([595.28,841.89]);const scale=Math.min((595.28-2*margin)/im.width,(841.89-2*margin)/im.height);page.drawImage(im,{x:(595.28-im.width*scale)/2,y:(841.89-im.height*scale)/2,width:im.width*scale,height:im.height*scale});await progress(10+Math.round(70*(i+1)/files.length));}await pdfOutput(out);
 }else if(['pdf-para-markdown','pdf-para-word','comparar-pdf'].includes(slug)){
  const texts:string[][]=[];
  for(const file of files){const doc=await pdfjs(file,o.password);try{if(doc.numPages>500)throw Error('Limite de 500 páginas.');const pages:string[]=[];for(let n=1;n<=doc.numPages;n++){const page=await doc.getPage(n);const content=await page.getTextContent();pages.push(content.items.map((item:any)=>item.str?(item.str+(item.hasEOL?'\n':' ')):'').join(''));await progress(10+Math.round(60*n/doc.numPages));}if(!pages.some(p=>p.trim()))throw Error('Nenhum texto extraível. Este documento precisa de OCR, ainda indisponível.');texts.push(pages);}finally{await doc.destroy();}}
  if(slug==='pdf-para-word'){const lib=await import('docx');const doc=new lib.Document({sections:[{children:texts[0].flatMap((text,i)=>[new lib.Paragraph({text:`Página ${i+1}`,pageBreakBefore:i>0}),...text.split('\n').map(line=>new lib.Paragraph(line))])}]});artifacts.push({name:'documento.docx',blob:await lib.Packer.toBlob(doc)});warnings.push('Texto editável; sem reconstrução de imagens, tabelas ou diagramação.');}
  else if(slug==='comparar-pdf'){let report='Comparação textual NoirPDF\n\n';let differences=0;const max=Math.max(texts[0].length,texts[1].length);for(let i=0;i<max;i++)if(texts[0][i]!==texts[1][i]){differences++;report+=`Página ${i+1}\n--- Original ---\n${texts[0][i]??'[sem página]'}\n+++ Comparado +++\n${texts[1][i]??'[sem página]'}\n\n`;}artifacts.push({name:'comparacao.txt',blob:new Blob([differences?report:'Nenhuma diferença textual encontrada.'],{type:'text/plain;charset=utf-8'})});warnings.push('Compara texto por página; diferenças visuais não são avaliadas.');}
  else{artifacts.push({name:'documento.md',blob:new Blob([texts[0].map((p,i)=>`<!-- Página ${i+1} -->\n\n${p}`).join('\n\n')],{type:'text/markdown;charset=utf-8'})});warnings.push('Extração textual, sem reconstrução semântica de tabelas, títulos ou imagens.');}
 }else if(['pdf-para-jpg','pdf-para-powerpoint'].includes(slug)){
  const doc=await pdfjs(files[0],o.password);try{if(doc.numPages>500)throw Error('Limite de 500 páginas.');for(const index of selection(o.pages,doc.numPages)){const page=await doc.getPage(index+1);const viewport=page.getViewport({scale:1.5});if(viewport.width*viewport.height>40_000_000)throw Error('Página grande demais para renderizar.');const canvas=document.createElement('canvas');canvas.width=viewport.width;canvas.height=viewport.height;await page.render({canvasContext:canvas.getContext('2d')!,viewport}).promise;const jpg=await new Promise<Blob>((res,rej)=>canvas.toBlob(b=>b?res(b):rej(Error('Falha de renderização.')),'image/jpeg',.9));artifacts.push({name:`pagina-${index+1}.jpg`,blob:jpg});await progress(10+Math.round(70*(index+1)/doc.numPages));}}finally{await doc.destroy();}
  if(slug==='pdf-para-powerpoint'){const {visualPptx}=await import('./browser-pptx');artifacts=[{name:'apresentacao.pptx',blob:await visualPptx(artifacts.map(a=>a.blob))}];warnings.push('Modo visual: páginas como imagens ajustadas a A4; conteúdo não editável.');}
 }else{
  const docs=[];for(const file of files){docs.push(await load(file));await progress(10+Math.round(20*docs.length/files.length));}const first=docs[0],count=first.getPageCount();let indices=selection(o.pages,count);let out=await PDFDocument.create();
  if(slug==='juntar-pdf'){for(let i=0;i<docs.length;i++){const pages=await out.copyPages(docs[i],docs[i].getPageIndices());for(const page of pages)out.addPage(page);await progress(30+Math.round(40*(i+1)/docs.length));}}
  else if(slug==='dividir-pdf'){const step=Number(o.every??1);if(!Number.isInteger(step)||step<1||step>count)throw Error('Quantidade de páginas por arquivo inválida.');for(let i=0;i<indices.length;i+=step){const part=await PDFDocument.create();const pages=await part.copyPages(first,indices.slice(i,i+step));pages.forEach(p=>part.addPage(p));await pdfOutput(part,`parte-${i/step+1}.pdf`);await progress(30+Math.round(50*(i+step)/indices.length));}}
  else{
   if(slug==='remover-paginas')indices=first.getPageIndices().filter(i=>!indices.includes(i));
   if(slug==='organizar-pdf'&&o.order){indices=o.order.map((n:number)=>n-1);if(!indices.every(n=>Number.isInteger(n)&&n>=0&&n<count))throw Error('Ordem de páginas inválida.');}
   if(!indices.length)throw Error('O resultado precisa conter pelo menos uma página.');
   if(['remover-paginas','extrair-paginas','organizar-pdf'].includes(slug)){const pages=await out.copyPages(first,indices);pages.forEach(p=>out.addPage(p));}
   else{out=first;const font=await out.embedFont(StandardFonts.Helvetica);for(const index of indices){const page=out.getPage(index),{width,height}=page.getSize();
    if(slug==='rodar-pdf'){const angle=Number(o.angle??90);if(![90,180,270].includes(angle))throw Error('Ângulo inválido.');page.setRotation(degrees((page.getRotation().angle+angle)%360));}
    if(slug==='recortar-pdf'){const m=Number(o.margin??24);if(!Number.isFinite(m)||m<0||m*2>=Math.min(width,height))throw Error('Margem de recorte inválida.');page.setCropBox(m,m,width-2*m,height-2*m);}
    if(['numeros-pagina','marca-dagua','editar-pdf','assinar-pdf'].includes(slug)){const text=slug==='numeros-pagina'?String(index+1):String(o.text||'NoirPDF').slice(0,1000);try{page.drawText(text,{x:slug==='marca-dagua'?width*.2:slug==='numeros-pagina'?width/2:50,y:slug==='marca-dagua'?height/2:slug==='numeros-pagina'?24:80,size:20,font,rotate:degrees(slug==='marca-dagua'?45:0),opacity:slug==='marca-dagua'?.25:1});}catch{throw Error('A fonte desta versão suporta caracteres latinos. Revise o texto informado.');}}
    await progress(30+Math.round(45*(index+1)/count));
   }
   if(slug==='formularios-pdf'){const form=out.getForm();if(!form.getFields().length)throw Error('O PDF não tem campos AcroForm.');const values=o.fields||{};if(!Object.keys(values).length)throw Error('Informe os valores dos campos em JSON.');for(const [name,value]of Object.entries(values)){const field=form.getField(name);if(field instanceof PDFTextField)field.setText(String(value));else if(field instanceof PDFCheckBox){if(value===true||value==='Yes')field.check();else field.uncheck();}else if(field instanceof PDFDropdown||field instanceof PDFRadioGroup)field.select(String(value));else throw Error('Tipo de campo não suportado nesta versão.');}form.updateFieldAppearances(font);}
   }
  }
  if(slug!=='dividir-pdf')await pdfOutput(out);
  if(slug==='comprimir-pdf')warnings.push('Reescrita com streams de objetos. Sem reamostragem de imagens ou três níveis de compressão; pode não reduzir o tamanho.');
  if(slug==='recortar-pdf')warnings.push('Recorte visual: o conteúdo subjacente permanece. Não use para ocultar dados sensíveis.');
  if(slug==='assinar-pdf')warnings.push('Assinatura visual digitada; sem certificado digital, identificação ou solicitação de assinatura.');
  if(slug==='editar-pdf')warnings.push('Sobreposição de texto; não edita nem remove o texto original.');
 }
 await progress(90);let result=artifacts[0];if(artifacts.length>1){const zip=new JSZip();artifacts.forEach(a=>zip.file(a.name,a.blob));result={name:'resultados.zip',blob:await zip.generateAsync({type:'blob',compression:'DEFLATE'})};}
 const original=files.reduce((n,f)=>n+f.size,0);if(slug==='comprimir-pdf'&&result.blob.size>=original)warnings.push('O arquivo não ficou menor. O original pode já estar otimizado.');
 return {filename:result.name,blob:result.blob,bytes:result.blob.size,original_bytes:original,warnings};
}
