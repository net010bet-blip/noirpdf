"""Local mode: run every minute (or use --once for a single pass)."""
import sys,time
from services.worker.tasks import cleanup
if __name__=='__main__':
    while True:
        cleanup()
        if '--once' in sys.argv: break
        time.sleep(60)
