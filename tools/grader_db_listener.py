import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "ClarkCSHWGrader.settings"

import psycopg2 as db
import select
from grader.models import Submission, AutograderResult
from datetime import datetime

TIMEOUT = 60
SUBMISSON_PAYLOAD = "submission"
AUTOGRADE_PAYLOAD = "autograded"

def get_conn():
    conn = db.connect("dbname=grader user=sam")
    conn.set_isolation_level(db.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN grader;")
    cur.close()
    return conn
    
def get_new_subs():
    return list(Submission.objects.filter(status=Submission.CH_SUBMITTED).order_by('sub_date'))

def run_autograder(sub):
    print ("Autograding %d..." % sub.id)
    
    ######
    #AUTOGRADER CODE HERE
    #sub.status = Submission.CH_AUTOGRADED
    #sub.save()
    #ar = AutograderResult(submission=sub, result=status, info_file=location)
    #ar.save()
    ######
    
if __name__ == "__main__":
    conn = get_conn()
    
    to_grade = get_new_subs()

    print ("Waiting for notifications on channel 'grader'")
    while True:
                
        
        print ("<%s> %d submissions to grade" % (str(datetime.now()), len(to_grade)))
        
        if len(to_grade) > 0:
            sub = to_grade.pop(0)
            run_autograder(sub)
            
            if len(to_grade) == 0:
                to_grade = get_new_subs()
        
        elif select.select([conn], [], [], TIMEOUT) != ([],[],[]):
            conn.poll()
            while conn.notifies:
                notification = conn.notifies.pop(0)
                if notification.payload == SUBMISSON_PAYLOAD:
                    to_grade = get_new_subs()
                
                
            
                
                
                
                
                
                
