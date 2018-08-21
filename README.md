# S3L Website 
Simply a copy and a way to version control the website
Because of the SU VPN we need to manually ssh into the server
and pull these changes down before the update get reflected.

## Updating this site
- To update this site there are several steps you need to take.
- First pul down the repo, make changes and commit it back here.
- Then, vpn into the SU network - you'll need to use your personal credentials
- Then ssh into s3l root account. Please contact Lisa or Jonathan for the credentials
- Once in the server, navigate to the s3l folder (should be directly under the root user acct home folder)
- Pull down the lates changes from the repo, i.e.: `git pull --rebase`
- Once this is complete, copy over all the changes from the s3l folder into the website folder, 
located under `/var/www/`
