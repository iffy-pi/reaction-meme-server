import os
import json
from apiutils.FileStorageClasses.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.configs.ServerConfig import ServerConfig

class RepoLocalFileStorage(JSONDBFileStorageInterface):
    """
    Stores the files to the repository project folder
    """
    def __init__(self):
        self.__dbFilePath = os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'db.json')

    def getJSONDB(self) -> dict:
        with open(self.__dbFilePath, 'r') as file:
            return json.load(file)

    def writeJSONDB(self, db:dict) -> bool:
        with open(self.__dbFilePath, 'w') as file:
            json.dump(db, file, indent=4)
        return True