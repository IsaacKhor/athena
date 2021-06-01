# Sprint 1 - notes

## Goals for previous sprint

- Examine what's salvageable from PASS source

Salvageable:
- Templating logic
- Model layer
- Some view layer
- DB schema

Not salvageable:
- url path matching
- DB connection
- CSS
- A significant chunk of HTML (divs everywhere)
- Shambles of an autograder system (with DB listeners, imagine)

- Se ewhat would be required to update from old system to th ecurrent one

Nothing, have to rewrite

- Try to get PASS running on my laptop

Impossible, not sure how I would even go about finding most of these libraries

- Mock LDAP so we don't need VPN or have to work with live user daat

Done, temporarily poked a hole thru zeus

- Check DB schema and what's currently there

Not alot of live data, mostly courses from 2015

- Check existing db migrations

Not much there


## Goals for current sprint

- Reimplement the model layer, with updates to parts that don't make sense
- Reimplement LDAP authentication and build new postgre db
- Reimplement coures page, assignment page, and downloads for them all
- Login page

## Meeting notes

Notes on testing out PASS's functionality with current TAs

- Interface seems a little dated, maybe a little refresh
- Easier way to create courses
- Create and update the admin panel
- Too many constraints not visible from admin panel
- More granular permissions on who's allowed to do what? TAs basically
  are the same is instructors, so why separate them