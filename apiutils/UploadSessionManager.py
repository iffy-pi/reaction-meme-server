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

    def newSession(self, itemId):
        """
        Adds a new session key for the given item ID, creates it with uuid
        :param itemId:
        :return: the session key
        """
        self.activeSessionKeys[str(itemId)] = str(uuid.uuid4())
        return self.activeSessionKeys[str(itemId)]

    def getSession(self, itemId):
        if itemId not in self.activeSessionKeys:
            return None
        return self.activeSessionKeys[str(itemId)]

    def clearSession(self, itemId):
        itemId = str(itemId)
        if itemId in self.activeSessionKeys:
            self.activeSessionKeys.pop(itemId)

    def clearAllSessions(self):
        self.activeSessionKeys.clear()



