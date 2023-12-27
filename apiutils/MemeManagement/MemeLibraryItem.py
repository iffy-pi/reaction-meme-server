from apiutils.MemeManagement.MemeMediaType import MemeMediaType
from localMemeStorageServer.utils.LocalStorageUtils import convertToLocal, getLocalVersionForCloudMeme
class MemeLibraryItem:
    def __init__(self, id:int=None, name:str=None, type: MemeMediaType =None, fileExt=None, tags:list[str]=None, cloudID=None, cloudURL=None):
        self.id = id
        self.name =     name
        self.tags =     tags
        self.fileExt =  fileExt
        self.cloudID =  cloudID
        self.cloudURL = cloudURL
        self.type = type

    @staticmethod
    def getDefaultName() -> str:
        return ''

    @staticmethod
    def getDefaultType() -> MemeMediaType:
        return MemeMediaType.UNKNOWN

    @staticmethod
    def getDefaultFileExt() -> str:
        return ''

    @staticmethod
    def getDefaultTags() -> list[str]:
        return []

    @staticmethod
    def getDefaultCloudID() -> str:
        return ''

    @staticmethod
    def getDefaultCloudURL() -> str:
        return ''

    def setProperty(self, id:int=None, name:str=None, type: MemeMediaType =None, fileExt:str=None, tags:list[str]=None, cloudID:str=None, cloudURL:str=None):
        """
        Set the property of the meme library item, any arguments left to None will not have the property value changed
        """
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if fileExt is not None:
            self.fileExt = fileExt
        if tags is not None:
            self.tags = tags
        if cloudID is not None:
            self.cloudID = cloudID
        if cloudURL is not None:
            self.cloudURL = cloudURL
        if type is not None:
            self.type = type

    def getID(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getTags(self) -> list[str]:
        return self.tags

    def getType(self) -> MemeMediaType:
        return self.type

    def getTypeString(self) -> str:
        return str(self.type.value)

    def getFileExt(self) -> str:
        return self.fileExt

    def __getCheckedCloud(self) -> tuple[str, str]:
        if not convertToLocal(self.cloudURL):
            return self.cloudID, self.cloudURL
        return getLocalVersionForCloudMeme(self.cloudID, self.cloudURL, self.fileExt)

    def getCloudID(self) -> str:
        cloudId, _ = self.__getCheckedCloud()
        return cloudId

    def getURL(self) -> str:
        _, cloudURL = self.__getCheckedCloud()
        return cloudURL

    def __str__(self):
        converted = '{}'.format(', convertedToLocal' if convertToLocal(self.cloudURL) else '')
        return f'Meme(id={self.id}, name="{self.name}", {self.type}, ext="{self.fileExt}", tags={self.tags}, cloudId={self.getCloudID()}, url={self.getURL()}{converted})'