# Requirements to Run #
Python 3.4

[Django 1.8](https://www.djangoproject.com/download/)

[Django Bootstrap3](http://django-bootstrap3.readthedocs.org/en/latest/index.html)

```
sudo pip3 install django-bootstrap3
sudo pip3 install django_admin_bootstrapped
sudo pip3 install django-autocomplete-light
```

# What has been done #
All of this uses Django. This is a good Django tutorial: [https://docs.djangoproject.com/en/1.8/intro/tutorial01/](https://docs.djangoproject.com/en/1.8/intro/tutorial01/)

## Database/Models ##
The project has four models

* **Course** - Stores a single section for a course in a single semester. Can have any number of students, TAs, and instructors.
* **Semester** - Stores a year and season (ie fall, spring, summer) of a semester, and some constants to display the semesters.
* **Assignment** - Stores an assignment, associated with a course.
* **Submission** - Stores a reference to a submission of an assignment. The actual submitted assignment will be stored on the filesystem.
* **Grade** - Stores a grade for a submission.

Additionally, I use the built in **User** model in Django to store students, TAs, and instructors.

"ER.png" contains an ER diagram which shows the relationships between all the models.

## Pages ##
All the pages are put together in *views.py*. The templates for each page have the same name as the methods in *views.py*. The pages are all pretty self descriptive, and the comments in *views.py* give more description.

## Submission Storage ###
Submissions are stored in the directory specified by *SUBMISSION_DIR* in *settings.py*. The submitted file for a specific assignment is in *<SUBMISSION_DIR>/<semester>/<course>/Sec.<section>/<assignment code>/<username>/<timestamp>/*

# What needs to be done #

##Different views for different users##
The home page should only show courses which the user is enrolled in, is a TA for, or is an instructor for. Some users shouldn't be allowed to view certain pages. Students, instructors, and TAs should also have different options on the course page (ie grade or submit assignments). Django can have different user groups, so maybe make instructor and student groups.

##Integrate users with LDAP##
Need to sync Django authentication system with current CS users.

##Add in auto-grader##
Need to communicate with auto-grader. For each submission, a record is currently stored in the database and the submitted file is put into the filesystem. Need a way to detect a submission being added to the database and the location of the file to be sent to the auto grader.

##More options for assignments##
* Enforce deadline or not
* Ability to change deadline
* When to release autograder results (immediately, after deadline, or manually by instructor/admin)

##Allow uploading files to assignment, grading, and course pages##
Instructors may want to add PDFs, images, text files, etc. to instructions for assignments, their grade, or for the course itself.
