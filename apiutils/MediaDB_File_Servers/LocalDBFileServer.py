import os
import json
from apiutils.MediaDB_File_Servers.MediaDBFileServer import MediaDBFileServer
DB_FILE = "C:\\local\\GitRepos\\reaction-meme-server\\db.json"

class LocalDBFileServer(MediaDBFileServer):
    def __init__(self):
        self.dbFilePath = DB_FILE

    def loadDBFromJSON(self):
        with open(self.dbFilePath, 'r') as file:
            return json.load(file)

    def writeJSONDB(self, db):
        with open(self.dbFilePath, 'w') as file:
            return json.dump(db, file, indent=4)