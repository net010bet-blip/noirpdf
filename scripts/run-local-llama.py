"""Optional loopback-only development provider using a real local GGUF model.
Install llama-cpp-python in a separate environment; no model is bundled/downloaded.
For production use an independently secured provider such as Ollama.
"""
import argparse,json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from llama_cpp import Llama
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--port',type=int,default=8099);args=p.parse_args()
model=Llama(model_path=args.model,n_ctx=4096,n_threads=2,verbose=False,chat_format='chatml');lock=threading.Lock()
class Handler(BaseHTTPRequestHandler):
 def respond(self,status,payload):
  encoded=json.dumps(payload,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(encoded)));self.end_headers();self.wfile.write(encoded)
 def do_GET(self):
  if self.path=='/v1/models':self.respond(200,{'object':'list','data':[{'id':'qwen-local','object':'model'}]})
  elif self.path=='/health':self.respond(200,{'status':'ready'})
  else:self.respond(404,{'error':'not found'})
 def do_POST(self):
  if self.path!='/v1/chat/completions':self.respond(404,{'error':'not found'});return
  try:
   count=int(self.headers.get('Content-Length','0'))
   if not 0<count<=200000:raise ValueError()
   body=json.loads(self.rfile.read(count));messages=body['messages']
   if not isinstance(messages,list):raise ValueError()
   with lock:result=model.create_chat_completion(messages=messages,temperature=0,max_tokens=min(int(body.get('max_tokens',256)),512))
   self.respond(200,result)
  except (ValueError,KeyError,TypeError):self.respond(400,{'error':'invalid request or context limit'})
  except Exception:self.respond(500,{'error':'local inference failed'})
 def log_message(self,*_args):pass
print('Local GGUF provider ready on loopback. Model contents and prompts are not logged.',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
