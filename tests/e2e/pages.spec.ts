import {test,expect} from '@playwright/test';
import path from 'node:path';
const url=process.env.PAGES_TEST_URL;
test.skip(!url,'Use PAGES_TEST_URL to test the static GitHub Pages build.');
const cases=[['juntar-pdf','pdf'],['dividir-pdf','zip'],['remover-paginas','pdf'],['extrair-paginas','pdf'],['organizar-pdf','pdf'],['digitalizar-pdf','pdf'],['comprimir-pdf','pdf'],['jpg-para-pdf','pdf'],['pdf-para-jpg','zip'],['pdf-para-word','docx'],['pdf-para-powerpoint','pptx'],['rodar-pdf','pdf'],['numeros-pagina','pdf'],['marca-dagua','pdf'],['recortar-pdf','pdf'],['editar-pdf','pdf'],['formularios-pdf','pdf'],['assinar-pdf','pdf'],['comparar-pdf','txt'],['pdf-para-markdown','md']];
for(const [slug,ext]of cases)test(`static browser engine: ${slug}`,async({page})=>{
 const requests:string[]=[];page.on('request',r=>{if(r.url().includes('/api/'))requests.push(r.url())});
 await page.goto(`${url}/ferramenta/${slug}/`);
 const source=['digitalizar-pdf','jpg-para-pdf'].includes(slug)?['photo.png']:slug==='formularios-pdf'?['form.pdf']:['juntar-pdf','comparar-pdf'].includes(slug)?['one.pdf','two.pdf']:['three.pdf'];
 await page.locator('input[type=file]').setInputFiles(source.map(f=>path.resolve('tests/fixtures',f)));
 if(slug==='remover-paginas'||slug==='extrair-paginas')await page.getByRole('textbox',{name:'Páginas (ex.: 1-3,5)'}).fill('2');
 if(slug==='organizar-pdf')await page.getByRole('textbox',{name:'Ordem final das páginas'}).fill('3,1,2');
 if(slug==='formularios-pdf')await page.locator('textarea').fill('{"name":"Maria"}');
 await page.getByRole('button',{name:/^Executar /}).click();
 await expect(page.getByText('Seu resultado está pronto.')).toBeVisible({timeout:30000});
 const event=page.waitForEvent('download');await page.getByRole('link',{name:/Baixar /}).last().click();const download=await event;
 await download.saveAs(`artifacts/browser-${slug}.${ext}`);expect(requests).toEqual([]);
 if(slug==='juntar-pdf'){await page.reload();await page.getByRole('button',{name:'Meu histórico'}).click();await expect(page.getByRole('link',{name:'Baixar',exact:true})).toBeVisible();const again=page.waitForEvent('download');await page.getByRole('link',{name:'Baixar',exact:true}).click();expect((await again).suggestedFilename()).toBe('resultado.pdf');}
});
test('static catalog, routes and no overflow',async({page})=>{for(const width of [375,768,1280,1920]){await page.setViewportSize({width,height:900});await page.goto(`${url}/`);await expect(page.locator('.tool-card')).toHaveCount(33);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:`artifacts/pages-${width}.png`,fullPage:true});}await page.goto(`${url}/ferramenta/proteger-pdf/`);await expect(page.getByRole('heading',{name:'Motor em desenvolvimento'})).toBeVisible();await expect(page.locator('input[type=file]')).toHaveCount(0);});
