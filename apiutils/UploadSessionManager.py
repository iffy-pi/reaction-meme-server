import uuid
from datetime import datetime, timedelta

class Session:
    def __init__(self, expiry:datetime, data:dict=None):
        self.expiry = expiry
        self.data = data

class UploadSessionManager:
    # 3 HOURS
    SESSION_LIFE_TIME_SECONDS = 3 * 60 * 60
    instance = None
    def __init__(self):
        self.activeSessionKeys = dict()

    @staticmethod
    def getInstance():
        if UploadSessionManager.instance is None:
            UploadSessionManager.instance = UploadSessionManager()
        return UploadSessionManager.instance


    def __newItem(self, kwargs:dict) -> Session:
        return Session(
            datetime.now() + timedelta(seconds=UploadSessionManager.SESSION_LIFE_TIME_SECONDS),
            dict(kwargs)
        )

    def newSession(self, **kwargs):
        """
        Creates a new upload key with the expiry date
        """
        newKey = str(uuid.uuid4())
        self.activeSessionKeys[newKey] = self.__newItem(kwargs)

        return newKey

    def getSessionData(self, sessionKey:str):
        if not self.validSession(sessionKey):
            raise Exception('Invalid Upload Session')

        return self.activeSessionKeys[sessionKey].data


    def validSession(self, sessionKey:str) -> bool:
        if sessionKey not in self.activeSessionKeys:
            return False

        expiryTime = self.activeSessionKeys[sessionKey].expiry
        if datetime.now() >= expiryTime:
            return False

        return True

    def clearExpiredSessions(self):
        for sessionKey in self.activeSessionKeys:
            expiryTime = self.activeSessionKeys[sessionKey].expiry
            if datetime.now() < expiryTime:
                continue

            self.activeSessionKeys.pop(sessionKey)

    def clearSession(self, sessionKey:str):
        if sessionKey in self.activeSessionKeys:
            self.activeSessionKeys.pop(sessionKey)

    def clearAllSessions(self):
        self.activeSessionKeys.clear()



