"""Bounded input validation; no database, network, or user-controlled executable."""
import sys,json,resource
resource.setrlimit(resource.RLIMIT_CPU,(8,8))
resource.setrlimit(resource.RLIMIT_AS,(384*1024**2,384*1024**2))
resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
from services.api.uploads import validate
from services.api.engines import DocumentError
try:
 validate(sys.argv[1],sys.argv[2],sys.argv[3]);print(json.dumps({'ok':True}))
except Exception as error:
 print(json.dumps({'error':str(error) if isinstance(error,DocumentError) else 'Arquivo inválido ou acima do limite de recursos de validação.'}));sys.exit(1)
