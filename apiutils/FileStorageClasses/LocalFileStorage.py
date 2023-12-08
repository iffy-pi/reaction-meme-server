import os
import json
from apiutils.FileStorageClasses.JSONDBFileStorage import JSONDBFileStorage
from apiutils.configs.ServerConfig import ServerConfig

class LocalFileStorage(JSONDBFileStorage):
    def __init__(self):
        self.__dbFilePath = os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'db.json')

    def getJSONDB(self):
        with open(self.__dbFilePath, 'r') as file:
            return json.load(file)

    def writeJSONDB(self, db:dict):
        with open(self.__dbFilePath, 'w') as file:
            return json.dump(db, file, indent=4)