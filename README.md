# TODOs before pusing to production #
set debug=False
make sure read/write permission in server
make sure www-data as owner
run python manage.py collectstatic

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

##Integrate users with LDAP##
Need to sync Django authentication system with current CS users.

##Add in auto-grader##
Need to communicate with auto-grader. For each submission, a record is currently stored in the database and the submitted file is put into the filesystem. Need a way to detect a submission being added to the database and the location of the file to be sent to the auto grader.

##More options for assignments##
* Enforce deadline or not
* Ability to change deadline (edit assignment)
* Add option to write description in markdown
* When to release autograder results (immediately, after deadline, or manually by instructor/admin)