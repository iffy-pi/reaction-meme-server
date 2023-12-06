import uuid

class UploadSessionManager:
    instance = None
    def __init__(self):
        self.activeSessionKeys = {}

    @staticmethod
    def getInstance():
        if UploadSessionManager.instance is None:
            UploadSessionManager.instance = UploadSessionManager()
        return UploadSessionManager.instance


    def newUploadKey(self, itemId:int):
        """
        Adds a new session key for the given item ID, creates it with uuid
        :param itemId:
        :return: the session key
        """
        uploadKey = str(uuid.uuid4())
        self.activeSessionKeys[uploadKey] = itemId
        return uploadKey

    def getIDForKey(self, uploadKey:str):
        """
        Retrieves the itemID mapped to the given upload key
        :param uploadKey:
        :return:
        """
        if uploadKey not in self.activeSessionKeys:
            return None
        return self.activeSessionKeys[uploadKey]
    def validUploadSession(self, uploadKey:str):
        return uploadKey in self.activeSessionKeys

    def clearUploadKey(self, uploadKey:str):
        if uploadKey in self.activeSessionKeys:
            self.activeSessionKeys.pop(uploadKey)

    def clearAllKeys(self):
        self.activeSessionKeys.clear()



