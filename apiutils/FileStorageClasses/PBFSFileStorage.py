import json

from apiutils.FileStorageClasses.JSONDBFileStorage import JSONDBFileStorage
from apiutils.FileStorageClasses.PushBulletFileServer import PushBulletFileServer

class PBFSFileStorage(JSONDBFileStorage):
    def __init__(self, accessToken, serverIdentifier):
        self.__pbfs = PushBulletFileServer(accessToken, serverIden=serverIdentifier, persistentStorage=True)
        self.__dbFilePath = "dbFiles/db.json"

    def getJSONDB(self):
        # If it does not exist on the server, initialize it and then return empty dictionary
        if not self.__pbfs.pathExistsInIndex(self.__dbFilePath):
            self.__pbfs.write(self.__dbFilePath, json.dumps({}).encode())
            return {}

        binary = self.__pbfs.read(self.__dbFilePath)
        return json.loads(binary.decode("utf-8"))

    def writeJSONDB(self, db:dict):
        self.__pbfs.write(self.__dbFilePath, json.dumps(db, indent=4))