import './globals.css';
import type {Metadata} from 'next';
export const metadata:Metadata={title:'NoirPDF — Seu PDF, do seu jeito',description:'Ferramentas gratuitas para organizar, converter e editar PDFs. Processamento real e privacidade por padrão.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="pt-BR"><body>{children}</body></html>}
