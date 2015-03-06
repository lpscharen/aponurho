APO Nu Rho
============
# Development Model
http://nvie.com/posts/a-successful-git-branching-model/

# Aliases
To create an alias:
<pre>git config --global alias.[your alias] '[the full command]'</pre>

## Alias examples:

git checkout [branch]
<pre>git co [branch] </pre>

git merge --no-ff [branch]:
<pre>git mrg [branch] </pre>

# Using south migration

## South Wiki
http://south.readthedocs.org/en/latest/

## South Summary
There are two steps that must be taken care of to complete a south migration.

The first step only applies to the user who directly edits the model. At this point the user will use the "schemamigration" command to generate a south file that is stored in the app_name/migrations folder. Each south migration file will have a tag with a migration number and brief synopsis of what the migration was for (ex: 0001intial.py).  The file will contain the db records and the changes made with that migration. 
After the user generates this file, it should be added to the git repo and committed (once the user has verified it works).

The second step must be carried out by the above user as well as any users who are operating on a different machine. The second command "migrate" will read the south migration from the file mentioned above and apply those changes to the database. In order to get this file, the other users will pull the develop branch which will give them the updated model file and the south migration file.  They will then only need to run the "migrate command" to update their local database and to tell south that there is a more up-to-date migration file. After running the command, the user should then merge the develop branch back into their working branch so that it contains the updated model changes.  
   
## Typical Useage
When you make model changes you have to update the migration history with this command (only run by committing user):
<pre>python manage.py schemamigration [app_name] --auto</pre>

<b>The two commands below update the local database using the south migration file (you must update your repo to get this file, if you did not originally create it with the above command)</b>

In order to apply the changes to the db (for a single app):
<pre>python manage.py migrate [app_name]</pre>

In order to apply the changes to the db (for all south apps):
<pre>python manage.py migrate</pre>


<b> If a user adds a field to models.py that already exists in the db</b>
The following command should be run once by the user who edited the model (then commit to repo):
<pre>python manage.py schemamigration [app] --add-field [Model.field]</pre>

<b> If a user adds a model with fields to models.py that already exists in the db</b>
<pre>python manage.py schemamigration [app] --add-field [Model.field] --add-field [Model.field] --add-model [Model]</pre>

In order to avoid an error with the following command you will then have to run the migration as fake (this should be all users once the repo is up to date):
<pre>python manage.py migrate [app] [migration number, ex: 0002] --fake</pre>

# Useful commands:
Clone Django app from github:
<pre>git clone https://github.com/itpir/aponurho.git </pre>

Make a local branch (this branches off of your last commit):
<pre>git checkout -b [branch] </pre>

Push new branch to github:
<pre>git add .
git push -u origin HEAD </pre>

Switch between existing branches:
<pre>git checkout [branch] </pre>

To commit specific files (local):
<pre>git add [files to commit]
git commit -m 'My commit message'</pre>

To commit all files in branch (local): 
<pre>git commit -a -m 'My commit message'</pre>

To update github repo after commit:
<pre>git pull
git push</pre>

To merge a branch:
<pre>
commit and/or push to github: git commit -a -m 'my message'
checkout branch you are merging into: git checkout [branch]
git fetch
git merge --no-ff [other_branch]
git push
</pre>

If you are done with your branch, delete it locally (never develop/master):
<pre>git branch -d [other_branch] </pre>

To delete on github (never develop/master):
<pre>git push origin :[other_branch] </pre>


