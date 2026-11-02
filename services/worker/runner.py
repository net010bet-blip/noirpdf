"""Bounded subprocess. Docker worker also runs without network and as non-root."""
import json, sys, resource
from pathlib import Path
from services.api.engines import run_engine, DocumentError
resource.setrlimit(resource.RLIMIT_CPU,(120,120))
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
resource.setrlimit(resource.RLIMIT_FSIZE,(200*1024**2,200*1024**2))
resource.setrlimit(resource.RLIMIT_NOFILE,(128,128))
base=Path(sys.argv[1]); options=json.load(sys.stdin)
try:
    # The trusted manifest retains upload order.
    paths=json.loads((base/'manifest.json').read_text()) if (base/'manifest.json').exists() else None
    if paths is None:
        from services.api.main import Session,Task
        with Session() as db: paths=[f['key'] for f in json.loads(db.get(Task,base.name).files)]
    def progress(value): (base/'progress').write_text(str(value))
    result=run_engine(sys.argv[2],[base/'input'/p for p in paths],options,base/'output',progress)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error':str(e) if isinstance(e,DocumentError) else 'O motor não conseguiu processar este documento.'})); sys.exit(1)
