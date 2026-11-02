import type {NextConfig} from 'next';
const pages=process.env.NEXT_PUBLIC_PROCESSING_MODE==='browser';
const config:NextConfig=pages?{output:'export',basePath:process.env.NEXT_PUBLIC_BASE_PATH||'',trailingSlash:true,images:{unoptimized:true}}:{async rewrites(){return [{source:'/api/:path*',destination:`${process.env.API_URL||'http://127.0.0.1:8000'}/api/:path*`}];}};
export default config;
