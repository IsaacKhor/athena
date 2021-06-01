# Sprint 1 - notes

## Goals for previous sprint

- Try to figure out who was involved with the previous operation

Sam, Catalin

- Ask around about who to contact to get admin credentials for the old system

Bayse: don't remember the passwords
Sam: no response
Ultimate solution: manually `psql` into the database, then `ALTER` myself 
into a superuser

- Try to get the source code to PASS

Simple git clone from athena, where it's hosted

- See what can be salvaged from it

Try to get it running, goal for this sprint

- Contant TAs involved and see what tehy would want from the system

Not much to say without anything working
Easy to diagnose what went wrong with autograder
Easy to test autograders against submissions
Place everything in clear directories with tools to access them so 
they can debug

- Design an API to interface betwene exsiting autograders and Athena

Since most autograding code has been ported to gradescope, try to maintain
compatability with the gradescope API with minimal changes

Maybe docker?


## Goals for current sprint

- Examine what's salvageable from PASS source
- Se ewhat would be required to update from old system to th ecurrent one
- Try to get PASS running on my laptop
- Mock LDAP so we don't need VPN or have to work with live user daat
- Check DB schema and what's currently there
- Check existing db migrations


## Meeting notes

Notes on testing out PASS's functionality with current TAs

- Interface seems a little dated, maybe a little refresh
- Easier way to create courses
- Create and update the admin panel
- Too many constraints not visible from admin panel
- More granular permissions on who's allowed to do what? TAs basically
  are the same is instructors, so why separate them