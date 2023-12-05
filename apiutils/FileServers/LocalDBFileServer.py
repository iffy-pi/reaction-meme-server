import os
import json
from apiutils.FileServers.MediaDBFileServer import MediaDBFileServer
from apiutils.configs.config import PROJECT_ROOT

class LocalDBFileServer(MediaDBFileServer):
    def __init__(self):
        self.dbFilePath = os.path.join(PROJECT_ROOT, 'data', 'db.json')

    def loadDBFromJSON(self):
        with open(self.dbFilePath, 'r') as file:
            return json.load(file)

    def writeJSONDB(self, db):
        with open(self.dbFilePath, 'w') as file:
            return json.dump(db, file, indent=4)