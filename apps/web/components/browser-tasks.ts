import {browserTools} from './browser-mode';
type Stored={id:string;tool:string;state:string;progress:number;created:number;expires:number;files:{key:string;name:string;bytes:number}[];inputs:File[];error?:string;result?:{filename:string;blob:Blob;bytes:number;original_bytes:number;warnings:string[]}};
const running=new Set<string>();const urls=new Map<string,string>();
function db():Promise<IDBDatabase>{return new Promise((res,rej)=>{const r=indexedDB.open('noirpdf-local-v1',1);r.onupgradeneeded=()=>r.result.createObjectStore('tasks',{keyPath:'id'});r.onsuccess=()=>res(r.result);r.onerror=()=>rej(Error('O armazenamento local não está disponível. Permita dados locais neste navegador.'));});}
async function transaction<T>(mode:IDBTransactionMode,fn:(store:IDBObjectStore)=>IDBRequest<T>):Promise<T>{const d=await db();try{return await new Promise<T>((res,rej)=>{const tx=d.transaction('tasks',mode);const req=fn(tx.objectStore('tasks'));let value:T;req.onsuccess=()=>value=req.result;tx.oncomplete=()=>res(value);tx.onerror=()=>rej(Error('Falha no armazenamento local. Verifique o espaço disponível.'));tx.onabort=tx.onerror;});}finally{d.close();}}
async function get(id:string){const task=await transaction('readonly',s=>s.get(id)) as Stored|undefined;if(!task)throw Error('Tarefa não encontrada neste navegador.');if(task.expires<Date.now()){await remove(id);throw Error('Os arquivos desta tarefa expiraram.');}return task;}
function put(t:Stored){return transaction('readwrite',s=>s.put(t));}
async function remove(id:string){if(urls.has(id)){URL.revokeObjectURL(urls.get(id)!);urls.delete(id);}await transaction('readwrite',s=>s.delete(id));}
function view(t:Stored){let result;if(t.result){if(!urls.has(t.id))urls.set(t.id,URL.createObjectURL(t.result.blob));const {blob,...meta}=t.result;result={...meta,url:urls.get(t.id)};}return {...t,inputs:undefined,result};}
async function clean(){const tasks=await transaction('readonly',s=>s.getAll()) as Stored[];for(const t of tasks){if(t.expires<Date.now())await remove(t.id);else if(['processing','queued'].includes(t.state)&&!running.has(t.id)){t.state='failed';t.error='O processamento foi interrompido ao fechar ou atualizar a página. Execute novamente.';t.inputs=[];await put(t);}}}
export async function browserApi(path:string,init?:RequestInit):Promise<any>{
 const method=init?.method||'GET';if(path==='/session'){await clean();return {mode:'browser',retention_seconds:3600};}
 if(path==='/tasks'&&method==='GET'){await clean();const tasks=await transaction('readonly',s=>s.getAll()) as Stored[];return tasks.sort((a,b)=>b.created-a.created).map(view);}
 if(path==='/tasks'&&method==='POST'){const {tool}=JSON.parse(init?.body as string);if(!browserTools.has(tool))throw Error('Este motor não está disponível no GitHub Pages.');await clean();const tasks=await transaction('readonly',s=>s.getAll());if(tasks.length>=30)throw Error('Limite de 30 tarefas locais. Exclua resultados anteriores.');const t:Stored={id:crypto.randomUUID(),tool,state:'created',progress:0,created:Date.now(),expires:Date.now()+3600000,files:[],inputs:[]};await put(t);return view(t);}
 const match=path.match(/^\/tasks\/([\w-]+)(?:\/(upload|execute|cancel))?$/);if(!match)throw Error('Operação local desconhecida.');const [,id,action]=match;
 if(method==='DELETE'){const t=await get(id);if(running.has(t.id))throw Error('Aguarde o processamento antes de excluir.');await remove(id);return null;}
 const t=await get(id);if(!action)return view(t);
 if(action==='upload'){
  if(!['created','ready'].includes(t.state))throw Error('Estado não aceita arquivos.');const incoming=(init?.body as FormData).getAll('files') as File[];const files=[...t.inputs,...incoming];if(!files.length||files.length>20||files.some(f=>f.size>50*1024**2)||files.reduce((n,f)=>n+f.size,0)>100*1024**2)throw Error('Limites: 20 arquivos, 50 MB por arquivo e 100 MB por tarefa.');
  const images=['jpg-para-pdf','digitalizar-pdf'].includes(t.tool);for(const f of incoming){if(images){if(!['image/jpeg','image/png','image/webp'].includes(f.type))throw Error('Use JPG, PNG ou WebP.');}else if(f.type!=='application/pdf'||new TextDecoder().decode(await f.slice(0,5).arrayBuffer())!=='%PDF-')throw Error('O conteúdo precisa ser um PDF válido.');}
  t.inputs=files;t.files=files.map(f=>({key:crypto.randomUUID(),name:f.name.replace(/.*[\\/]/,''),bytes:f.size}));t.state='ready';await put(t);return view(t);
 }
 if(action==='execute'){
  if(t.state!=='ready')throw Error('Selecione arquivos antes de executar.');const {options}=JSON.parse(init?.body as string);t.state='queued';running.add(t.id);await put(t);
  setTimeout(async()=>{try{t.state='processing';await put(t);const {runBrowserEngine}=await import('./browser-engine');t.result=await runBrowserEngine(t.tool,t.inputs,options,async n=>{t.progress=Math.max(t.progress,Math.min(95,n));await put(t);await new Promise(r=>setTimeout(r,0));});t.state='completed';t.progress=100;}catch(e){t.state='failed';t.error=(e as Error).message||'Não foi possível processar o documento.';}finally{t.inputs=[];try{await put(t);}finally{running.delete(t.id);}}},0);
  return view(t);
 }
 if(action==='cancel'){if(running.has(t.id))throw Error('Cancelamento indisponível durante processamento.');t.state='cancelled';t.inputs=[];await put(t);return view(t);}
 throw Error('Operação não disponível.');
}
