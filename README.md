# TODOs before pusing to production #
set debug=False

make sure read/write permission in server

make sure www-data as owner

run python manage.py collectstatic

run python manage.py ldap_sync_users (optional)

# Requirements to Run #
Python 3.4

[Django 1.8](https://www.djangoproject.com/download/)

[Django Bootstrap3](http://django-bootstrap3.readthedocs.org/en/latest/index.html)

[Django datetime widget](https://github.com/asaglimbeni/django-datetime-widget)

[Python markdown](https://pypi.python.org/pypi/Markdown)

```
sudo pip3 install django-bootstrap3
sudo pip3 install django_admin_bootstrapped
sudo pip3 install django-autocomplete-light
pip install django-datetime-widget
sudo pip3 install markdown
pip install django-python3-ldap
```
Need to have "db_config.py" file in root directory. For development, this can have the following code:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
```

In production, this file has the info for connecting to the postgres database.

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

##Change submissions to less complex path##
Should just be stored in directory with submission ID as name

##Automatically create email addresses##
Should set user's email to "username@clarku.edu"

##Allow file uploading when grading##

##Error handling##
Currently any errors (ie courses which don't exist, etc) will return "Internal server error".

##Add in auto-grader##
Need to communicate with auto-grader. For each submission, a record is currently stored in the database and the submitted file is put into the filesystem. Need a way to detect a submission being added to the database and the location of the file to be sent to the auto grader (database listener)