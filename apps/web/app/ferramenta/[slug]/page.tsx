import Studio from '../../../components/Studio';
import catalog from '../../../../../packages/shared/catalog.json';
import {notFound} from 'next/navigation';
export function generateStaticParams(){return catalog.map(t=>({slug:t.slug}))}
export default async function Tool({params}:{params:Promise<{slug:string}>}){const {slug}=await params;if(!catalog.some(t=>t.slug===slug))notFound();return <Studio slug={slug}/>}
