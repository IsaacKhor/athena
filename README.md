# Athena Homework Submission System

Dev and user documentation in `/docs`

## Requirements

- Django 3.0 or above
- Python 3.8 or above
- PostgreSQL
- Redis
- Ability to access the OpenLDAP server
- Sphinx

## Setup dev environment

Confirmed to work on Ubuntu 20.04

- Clone the repo
- Setup virtualenv with python
- Install the requirements in `requirements.txt`
- Set up PostgreSQL server
- Set up Redis server
- Modify `settings.py` to point to the dev PostgreSQL / Redis servers
  when environment variable / real variable in the file is `True`
- Make sure you have access to the LDAP server hosting the accounts, do
  this by setting up an OpenLDAP server on your machine, the scope of which
  is beyond this guide

## Running dev environment

- `./manage.py ldap_sync_users` to synchronise LDAP entries
- `./manage.py ldap_promote <user>` on a user you have access to
- Make sure postgresql and redis servers are running
- `./manage.py qcluster` to start up a job running cluster
- `./mange.py runserver` to start the dev server
- Any changes you make will be picked up live and the server will
  reload with these new changes

## Deploy notes

- Ideally this is run through Apache/nginx
- Make sure the user running the django application has write access
  to the local directory and to `/tmp`
- Make sure that there is sufficient compute resources, so allocate more
  CPU/RAM to the VM running this thing
- Generate documentation with `make html` (uses sphinx)
- Git push works just fine, although may not want to push directly into prod