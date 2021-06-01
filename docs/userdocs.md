# Course creation

Permission required: superuser

Each course belongs to a semester, so if a semester doesn't already exist for
the course, then create that first.

Once that's done, click the create course button in the admin panel. 

# Assignment creationg

Go into a course, click the add button. The important bit is that there are
2 possible grading systems: manual grading and autograding.

With manual grading, an instructor or TA can view all assignments and mannually
assign each one a grade.

With autograding, refer to the autograde.md file to see the specs and design
of the autograder. The API is designed to be compatible with gradescope
to the greatest extent possible.

When autograde is chosen, each submission will automatically trigger the
autograder to run, which will then in turn get sent to a runqueue for each
submission. When the autograder is done, it triggers a callback in the
application which will then update the DB with the grade parsed from the
autograder output and add all the artifacts produced to the submission
files.