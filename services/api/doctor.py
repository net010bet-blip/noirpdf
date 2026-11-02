"""Configuration report, without credentials or document contents."""
import json,sys,os
from .main import CATALOG
from .advanced import readiness

def main():
    tools=[{'tool':t['slug'],'ready':readiness(t['slug'])[0],'reason':readiness(t['slug'])[1]} for t in CATALOG]
    print(json.dumps({'tools':tools,'ai_configured':bool(os.getenv('AI_BASE_URL') and os.getenv('AI_MODEL'))},ensure_ascii=False,indent=2))
    if '--strict' in sys.argv and any(not t['ready'] for t in tools if t['tool'] not in ('resumir-pdf','traduzir-pdf')):sys.exit(1)
if __name__=='__main__':main()
