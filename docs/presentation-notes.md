# Simple notes


- Main idea: replicate the autograding functionality of gradescope
- How hard could it possibly be?

- Found out that we acutally had an existing system another person built
- Last updated 2015, 6 years ago
- Webdev has come a long way since, it doesn't even run on Ubuntu 2004
- Most modules no longer exist

- After some investigation into if the code was salvageable
- Also the Not Invented Here syndrome

Safe:
- Reimplement the whole app in python3/django3/bootstrap5
- Fully functioning web app with courses, assignments
- Administrative capability
- No loss in features

Expected:
- Adaptive
- Minor UI redesign to make it look better
- Fully automated autograder

Reach:
- Pretty UI like gradescope that keeps track of it live
- Docker containers/chroot envionments for security/isolation

Customer interactions:
- Mainly talked to the TAs working on the autograder
- The before time - manual autograding
- Lots of discussion on how best to design the autograding API
- Autograders take up to 15 minutes to run
- Using java, python, etc
- Easy layers of adaptation for existing autograding code and new gradescope code
- Compatibility with gradescope infrastructure
- Reports stored in easily accessible places for ease of access

Artefacts
- UML
- autogen docs
- Lots more documentation

SCM: 
- Git
- Allowed me to revert some pretty big mistakes
- DB backups
- Push to prod XD

