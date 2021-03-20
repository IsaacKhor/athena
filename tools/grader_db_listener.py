import os, sys, subprocess, glob, re, time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "ClarkCSHWGrader.settings"

#import psycopg2 as db
import select
from grader.models import Submission, AutograderResult
from datetime import datetime

RELOAD_TIME = 60
GRADER_TIMEOUT = 30*60
SUBMISSON_PAYLOAD = "submission"
AUTOGRADE_PAYLOAD = "autograded"

SCORE_RE = re.compile("\s+\*\s+Total Grade\s+(\d+)/\d+\s*")

"""
def get_conn():
    conn = db.connect("dbname=grader user=sam")
    conn.set_isolation_level(db.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN grader;")
    cur.close()
    return conn
"""
    
def get_new_subs():
    return list(Submission.objects.filter(status=Submission.CH_TO_AUTOGRADE).order_by('sub_date'))

def run_autograder(sub):
    print ("Autograding %d..." % sub.id)
    
    #Run the autograder
    subprocess.call(["AutoGrader/bin/AutoGrader", "-u", sub.student.username, "-n", sub.assignment.code, "-s", sub.get_directory()], timeout=GRADER_TIMEOUT)
    
    #Get the score from the report
    score = 0
    for path, dirs, fnames in os.walk(sub.get_directory(subdir=Submission.REPORT_DIR)):
        for fname in fnames:
            if re.match(".*-test.txt$", fname):
                f = open(os.path.join(path, fname))
                for line in f:
                    m = SCORE_RE.match(line)
                    if m:
                        score = float(m.group(1))
                        break
                f.close()
    
    #Save the autograder result
    sub.status = Submission.CH_AUTOGRADED
    sub.save()
    ar = AutograderResult(submission=sub, score=score, visible=False, result_dir=os.path.join(sub.get_directory(), "report"))
    ar.save()
    
if __name__ == "__main__":
    #conn = get_conn()

    print ("Waiting for notifications on channel 'grader'")
    while True:
        
        to_grade = get_new_subs()
                
        print ("<%s> %d submissions to grade" % (str(datetime.now()), len(to_grade)))
        
        if len(to_grade) > 0:
            sub = to_grade.pop(0)
            run_autograder(sub)
        else:
            time.sleep(RELOAD_TIME)
            
        """
        elif select.select([conn], [], [], TIMEOUT) != ([],[],[]):
            conn.poll()
            while conn.notifies:
                notification = conn.notifies.pop(0)
                if notification.payload == SUBMISSON_PAYLOAD:
                    to_grade = get_new_subs()
        """
                
                
            
                
                
                
                
                
                
