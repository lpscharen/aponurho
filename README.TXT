The default django is installed and configured to work with sqlite.

Please change setting.py to meet your needs.
especially secret key.

The admin interface enabled by default - 
login: admin
password: admin

Please change it as well.

Default django installation is svn rev 7811 

to use django-svn version use: ( from shell )

export PYTHONPATH=/home/django/django_src

before calling python.

If you want to use 0.96 version use:

export PYTHONPATH=/home/django/Django-0.96



If you need to change django version - edit htaccess in your public_html dir ( 
no more apache directive changes)

adjust your htaccess file for use other django version like:

PythonPath "['/home/share/Django-1.2.3']  + ['/home/aponurho'] + sys.path"

To use svn  ( updated daily ) on website edit 
PythonPath "['/home/share/django_src']+ ['/home/aponurho'] + sys.path"



