# Backup Information
The back_up_json_db.py is a python file which takes the current version of the JSON DB (gotten from the Productioon PushBullet server device) and saves it into the configured backup location.

This was introduced to provide another option for database backups, in the case something goes completely wrong with PushBullet or some other thing.

As of now the script is designed to run daily in the background using the windows task scheduler. This was pretty simple to configure. Just use the following:
For the program, enter:
```
C:\local\GitRepos\reaction-meme-server\venv\Scripts\python.exe
```

For the arguments enter:
```
"C:\Users\omnic\local\GitRepos\reaction-meme-server\server-void\backups\back_up_json_db.py"
```