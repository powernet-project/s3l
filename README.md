# S3L Website 
Simply a copy and a way to version control the website. Because of the SU VPN we need to manually ssh into the server
and pull these changes down before the update can get reflected on the site.

## Making changes to the S3L site
After you have the repo pulled down locally (your personal machine), you can simply open the `index.html` file with a browser to view it. Then open the file with your favorite editor and hack at it.

A better way however, is to:
```
cd www/
python -m http.server <- assuming OSX w/ python 3
```

Running the site in the localhost makes it easier to triage issues and see what's happening.

## Putting your above changes on the S3L server
- To update this site there are several steps you need to take.
- First pull down the repo, make changes and commit it back here.
- Then, vpn into the SU network - you'll need to use your personal SU credentials
- Then `ssh` into S3L `root` account. Please contact Lisa or Jonathan for the credentials
- Once in the server, navigate to the s3l folder (should be directly under the root user acct home folder)
- Pull down the latest changes from the repo, i.e.: `git pull --rebase`
- Once this is complete, copy over all the changes from the s3l folder into the website folder, 
located under `/var/www/`
- The easiest way to perform the final update/copy is run the alias'ed command: `updates3l`
- IMPORTANT: Please remember to commit your changes back to GitHub if you have any. But you shouldn't!! All your changes should come from your account on your machine and not the one in the S3L server.
- Committing your changes needs to be done under the version controlled folder (under `s3l/www` and not `/var/www/`)
- To do this, run:
```
git commit -am "My important update message"
git push
```
Jonathan trying to get this through Lisa's thick head
Making sure I remember that I have to be in the right directory in the terminal, but also then open the text editor (called Sublime)
git commit is typed into the terminal
after you change any files you go back to the terminal to commit them.
(file menu, save)