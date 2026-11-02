import os,time,shutil
from celery import Celery
app=Celery('noirpdf',broker=os.getenv('REDIS_URL','redis://redis:6379/0'))
app.conf.update(task_ignore_result=True,worker_prefetch_multiplier=1,task_acks_late=True,beat_schedule={'expire-files':{'task':'noirpdf.cleanup','schedule':60.0}})
@app.task(name='noirpdf.process')
def process(tid,options):
    from services.api.main import process_task
    process_task(tid,options)
@app.task(name='noirpdf.cleanup')
def cleanup():
    from services.api.main import Session,Task,DATA
    with Session() as db:
        for t in db.query(Task).filter(Task.expires<time.time(),Task.state!='expired'):
            shutil.rmtree(DATA/t.id,ignore_errors=True); t.state='expired'; t.files='[]'; t.result=None
        db.commit()
