import os
import json
from apiutils.FileStorage.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.configs.ServerConfig import ServerConfig, ProjectEnvironment

class LocalFileStorage(JSONDBFileStorageInterface):
    """
    Stores the files to the repository project folder
    """
    def __init__(self):
        self.__dbFilePath = ServerConfig.path('data', 'db.json')
        if ServerConfig.PROJECT_ENVIRONMENT == ProjectEnvironment.TESTING:
            self.__dbFilePath = ServerConfig.path('data', 'testing_db.json')

    def getJSONDB(self) -> dict:
        with open(self.__dbFilePath, 'r') as file:
            return json.load(file)

    def writeJSONDB(self, db:dict) -> bool:
        with open(self.__dbFilePath, 'w') as file:
            json.dump(db, file, indent=4)
        return True