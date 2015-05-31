# What has been done #
All of this uses Django. This is a good Django tutorial: [https://docs.djangoproject.com/en/1.8/intro/tutorial01/](https://docs.djangoproject.com/en/1.8/intro/tutorial01/)

## Database/Models ##
The project has four models

* **Course** - Stores a single section for a course in a single semester. Can have any number of students, TAs, and instructors.
* **Assignment** - Stores an assignment, associated with a course.
* **Submission** - Stores a reference to a submission of an assignment. The actual submitted assignment will be stored on the filesystem.
* **Grade** - Stores a grade for a submission.

Additionally, I use the built in **User** model in Django to store students, TAs, and instructors.

"ER.png" contains an ER diagram which shows the relationships between all the models.

## Pages ##
All the pages are put together in *views.py*. The templates for each page have the same name as the methods in *views.py*. The pages are all pretty self descriptive, and the comments in *views.py* give more description.

# What needs to be done #

##Store submissions on filesystem##
Right now we have access to submitted files, but they're not saved. They should be saved on the filesystem in some human readable directory. The directory structure should be something like */semester/course/section/assignment/user/submission.zip*

##Make login page##
Right now I have dropdown menus to choose user for submitting/grading assignments. There should be a login page which saves a cookie with the user ID, like a normal website.

##Different views for different users##
The home page should only show courses which the user is enrolled in, is a TA for, or is an instructor for. Some users shouldn't be allowed to view certain pages. Students, instructors, and TAs should also have different options on the course page (ie grade or submit assignments). Django can have different user groups, so maybe make instructor and student groups.

##Integrate users with LDAP##
Need to sync Django authentication system with current CS users.

##Add in auto-grader##
Need to communicate with auto-grader

##Way to create courses##
Make a way to create courses. Maybe make it easier than filling out web form? Like upload an excel file of all courses?

Related - make easy page for submitting grades, easy page for downloading assignments.