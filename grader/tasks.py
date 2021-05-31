from django_q.tasks import async_task, result
from django.conf import settings
from grader.models import AutograderResult
import json, subprocess

from pathlib import Path

from grader.models import Submission, Assignment

def autograde_complete(task):
    print(f'{task}, {task.result}')
    agid = int(task.result.args[-1])
    ag_res = AutograderResult.objects.get(pk=agid)
    print(f'{ag_res}')
    submission = ag_res.submission
    submission.status = Submission.CH_AUTOGRADED

    if not task.success:
        ag_res.score = 0
        ag_res.autograde_success = False
    else:
        results_json_file = submission.get_report_dir() / Submission.RESULTS_FILENAME
        with open(results_json_file, 'r') as f:
            results = json.load(f)
        print(results)

        ag_res.score = results['score']
        ag_res.autograde_success = True
    
    ag_res.save()


def autograde_submission(sub, subzip):
    asgn = sub.assignment

    if not subzip or asgn.autograde_mode != Assignment.AUTOGRADE:
        # TODO Complain very loudly
        return
    
    autograder_zip = Path(asgn.autograder_path).resolve()
    submission_zip = Path(subzip).resolve()

    if not autograder_zip:
        return

    # Here's what we need to do to autograde an assignment:
    # 1. Find a nice safe space for us to work in. Ideally, this is a docker
    #    container, a chroot environment, etc, but for now just
    #    use BASE = /tmp/athena-autograder/<submission_id>/
    # 2. Create that directory, hand off to the autograde script, passing in
    #     - BASE
    #     - Path to autograder zip
    #     - Path to submission zip
    #     - Path to submission reports directory
    #     It will:
    #     - Unzip the autograder there
    #     - Run the `run_autograder` script
    #     - The script will run everything and leave output at <base>/output/
    #     - The output directory MUST contain a `results.json` file
    #     - Copy everything there into the submission reports directory
    #     - Clean everything up, delete everything
    # 3. Parse the results.json, extract the grade
    # 4. Update grade in DB, update submission state

    # Step 1: Find a nice safe space to work in
    base = Path('/tmp/athena-autograder') / str(sub.id)
    base.mkdir(parents=True, exist_ok=True) # Make sure it exists

    # Create reports directory if it doesn't already exist
    reports_dir = sub.get_report_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)
    script_out = sub.get_autograde_output_log()
    if not script_out.exists():
        f = open(script_out, 'w')
        f.close()

    # Create autograde result now
    ag_res = AutograderResult(submission=sub, result_dir=reports_dir, autograde_success=False)
    ag_res.save()

    print(f'Running: {settings.AUTOGRADE_SCRIPT}, {base}, {autograder_zip}, {submission_zip}, {reports_dir}')
    print(f'Log at {script_out}')

    # Step 2: hand off to autograde script
    tid = async_task('subprocess.run', [
        settings.AUTOGRADE_SCRIPT,
        base,
        autograder_zip,
        submission_zip,
        reports_dir,
        script_out,
        str(ag_res.id),
    ], capture_output=True, hook='grader.tasks.autograde_complete')


    return tid
