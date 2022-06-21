@ECHO OFF
SET PYTHONDONTWRITEBYTECODE=1
SET FLASK_APP=./webserver.py 
SET FLASK_ENV=development
SET SECRET_KEY=07f5809c4084f1bb178c7cf6fdfb0abd
SET WEBSITE_NAME=B15 Server
flask createdb
REM ECHO Running with Gevent...
REM flask run_with_gevent
flask run 
EXIT