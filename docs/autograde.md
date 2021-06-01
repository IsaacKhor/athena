# Autograder API

API compatability is maintained with gradescope to the greatest extent possible.
Here's how it works when the autograder is triggered:

## Assumptions

1. The autograder is a singular zip file that contains a `run_autograder` 
   executable file
2. The submission is also a single zip file that contains the submission
3. No validation is done on the submission zip; if it contains an unzip attack
   then we're screwed (TODO: fix that)
4. There is no infinite loop detection -- if your code runs forever, nothing
   will catch it and it will sit there and consume CPU resources forever

## Autograding process

Some of this is in the `autograder/autograde.sh` script:

1. The student submits a `.zip` to the assignment
2. The autograder is triggered, it gets put into the qcluster queue
3. We create a new directory (by default in `/tmp/athena-autograder`) and
   set that as the working directory
4. Create the following directories: `submission`, `result`
5. The submission is unzipped into `submission`, just as it is in gradescope
6. We call `run_autograder`
7. The `run_autograder` executable grades the assignment
8. Everything in `result` is treated as output artifacts and copied to the
   directory where submission artifacts are stored
9. The base directory is cleaned up

## Autograder output

The output of the autograder can take whatever shape it wants, subject to
the following constraints:

- ONLY files in `BASE/results/` will be retained and given back to the user
- There MUST exist a `result/results.json` file with a `score` field (which
  is then parsed by the app as the score received for the assignment)
- The timelimit of the autograder is set in `settings.py`