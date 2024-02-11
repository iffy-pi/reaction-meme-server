import json

from apiutils.FileStorage.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.FileStorage.PushBulletFileServer import PushBulletFileServer

class PBFSFileStorage(JSONDBFileStorageInterface):
    def __init__(self, accessToken, serverIdentifier):
        self.__pbfs = PushBulletFileServer(accessToken, serverIden=serverIdentifier, persistentStorage=True)
        self.__dbFilePath = "dbFiles/db.json"

    def __uploadDBFile(self, db):
        return self.__pbfs.write(self.__dbFilePath, json.dumps(db, indent=4), deleteOldVersion=False)

    def getJSONDB(self) -> dict:
        # If it does not exist on the server, initialize it and then return empty dictionary
        if not self.__pbfs.pathExistsInIndex(self.__dbFilePath):
            self.__uploadDBFile({})
            return {}

        binary = self.__pbfs.read(self.__dbFilePath)
        return json.loads(binary.decode("utf-8"))

    def writeJSONDB(self, db:dict) -> bool:
        path = self.__uploadDBFile(db)
        return path is not None