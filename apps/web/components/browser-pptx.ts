import JSZip from 'jszip';
import {basePath} from './browser-mode';
/** Visual PPTX: clones an original empty slide template; embeds each rendered page. */
export async function visualPptx(images:Blob[]):Promise<Blob>{
 const response=await fetch(`${basePath}/presentation-template.pptx`);if(!response.ok)throw Error('Não foi possível carregar o modelo de apresentação.');
 const zip=await JSZip.loadAsync(await response.arrayBuffer());const slide=await zip.file('ppt/slides/slide1.xml')!.async('string');const rel=await zip.file('ppt/slides/_rels/slide1.xml.rels')!.async('string');
 let presentation=await zip.file('ppt/presentation.xml')!.async('string');let relationships=await zip.file('ppt/_rels/presentation.xml.rels')!.async('string');let types=await zip.file('[Content_Types].xml')!.async('string');
 relationships=relationships.replace(/<Relationship\b[^>]*Type="[^"]*\/slide"[^>]*\/>/g,'');
 types=types.replace(/<Override\b[^>]*PartName="\/ppt\/slides\/slide\d+\.xml"[^>]*\/>/g,'');
 if(!types.includes('Extension="jpg"'))types=types.replace('</Types>','<Default Extension="jpg" ContentType="image/jpeg"/></Types>');
 const ids:string[]=[];for(let i=0;i<images.length;i++){const n=i+1;zip.file(`ppt/slides/slide${n}.xml`,slide);zip.file(`ppt/slides/_rels/slide${n}.xml.rels`,rel.replace('../media/image1.png',`../media/page${n}.jpg`));zip.file(`ppt/media/page${n}.jpg`,images[i]);ids.push(`<p:sldId id="${256+i}" r:id="rIdNoirSlide${n}"/>`);relationships=relationships.replace('</Relationships>',`<Relationship Id="rIdNoirSlide${n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide${n}.xml"/></Relationships>`);types=types.replace('</Types>',`<Override PartName="/ppt/slides/slide${n}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>`);}
 presentation=presentation.replace(/<p:sldIdLst>[\s\S]*?<\/p:sldIdLst>/,`<p:sldIdLst>${ids.join('')}</p:sldIdLst>`);
 zip.file('ppt/presentation.xml',presentation);zip.file('ppt/_rels/presentation.xml.rels',relationships);zip.file('[Content_Types].xml',types);
 return zip.generateAsync({type:'blob',compression:'DEFLATE',mimeType:'application/vnd.openxmlformats-officedocument.presentationml.presentation'});
}
