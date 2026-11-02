export const browserMode=process.env.NEXT_PUBLIC_PROCESSING_MODE==='browser';
export const basePath=process.env.NEXT_PUBLIC_BASE_PATH||'';
export const browserTools=new Set(['juntar-pdf','dividir-pdf','remover-paginas','extrair-paginas','organizar-pdf','digitalizar-pdf','comprimir-pdf','jpg-para-pdf','pdf-para-jpg','pdf-para-word','pdf-para-powerpoint','rodar-pdf','numeros-pagina','marca-dagua','recortar-pdf','editar-pdf','formularios-pdf','assinar-pdf','comparar-pdf','pdf-para-markdown']);
