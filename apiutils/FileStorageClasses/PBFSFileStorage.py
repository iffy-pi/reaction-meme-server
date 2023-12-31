import json

from apiutils.FileStorageClasses.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.FileStorageClasses.PushBulletFileServer import PushBulletFileServer

class PBFSFileStorage(JSONDBFileStorageInterface):
    def __init__(self, accessToken, serverIdentifier):
        self.__pbfs = PushBulletFileServer(accessToken, serverIden=serverIdentifier, persistentStorage=True)
        self.__dbFilePath = "dbFiles/db.json"

    def getJSONDB(self) -> dict:
        # If it does not exist on the server, initialize it and then return empty dictionary
        if not self.__pbfs.pathExistsInIndex(self.__dbFilePath):
            self.__pbfs.write(self.__dbFilePath, json.dumps({}).encode())
            return {}

        binary = self.__pbfs.read(self.__dbFilePath)
        return json.loads(binary.decode("utf-8"))

    def writeJSONDB(self, db:dict) -> bool:
        path = self.__pbfs.write(self.__dbFilePath, json.dumps(db, indent=4))
        return path is not None