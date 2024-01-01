from apiutils.MemeManagement.MemeMediaType import MemeMediaType, memeMediaTypeToString, memeMediaTypeToInt, \
    stringToMemeMediaType
from localMemeStorageServer.utils.LocalStorageUtils import cloudMemeNeedsToBeConvertedToLocal, getLocalVersionForCloudMeme
class MemeContainer:
    """
    Class used as a data container for meme information. It is not connected to the meme library or the meme database that created it.
    """
    def __init__(self, id:int=None, name:str=None, mediaType: MemeMediaType =None, fileExt=None, tags:list[str]=None, cloudID=None, cloudURL=None, mediaTypeStr:str=None):
        self.id = id
        self.name =     name
        self.tags =     tags
        self.fileExt =  fileExt
        self.cloudID =  cloudID
        self.cloudURL = cloudURL
        self.mediaType = None

        if mediaTypeStr is not None:
            self.mediaType = stringToMemeMediaType(mediaTypeStr)

        if mediaType is not None:
            self.mediaType = mediaType

    @staticmethod
    def getDefaultName() -> str:
        return ''

    @staticmethod
    def getDefaultMediaType() -> MemeMediaType:
        return MemeMediaType.UNKNOWN

    @staticmethod
    def getDefaultMediaTypeString() -> str:
        return memeMediaTypeToString(MemeMediaType.UNKNOWN)

    @staticmethod
    def getDefaultMediaTypInt() -> int:
        return memeMediaTypeToInt(MemeMediaType.UNKNOWN)

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

    def setProperty(self, id:int=None, name:str=None, mediaType: MemeMediaType =None, fileExt:str=None, tags:list[str]=None, cloudID:str=None, cloudURL:str=None):
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
        if mediaType is not None:
            self.mediaType = mediaType

    def getID(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getTags(self) -> list[str]:
        return self.tags

    def getMediaType(self) -> MemeMediaType:
        return self.mediaType

    def getMediaTypeString(self) -> str:
        if self.mediaType is None:
            return None
        return memeMediaTypeToString(self.mediaType)

    def getMediaTypeInt(self) -> int:
        if self.mediaType is None:
            return None
        return memeMediaTypeToInt(self.mediaType)

    def getFileExt(self) -> str:
        return self.fileExt

    def __getCheckedCloud(self, autoConvertToLocal:bool) -> tuple[str, str]:
        if not (autoConvertToLocal and cloudMemeNeedsToBeConvertedToLocal(self.cloudURL)):
            return self.cloudID, self.cloudURL
        return getLocalVersionForCloudMeme(self.cloudID, self.cloudURL, self.fileExt)

    def getCloudID(self, autoConvertToLocal=True) -> str:
        cloudId, _ = self.__getCheckedCloud(autoConvertToLocal)
        return cloudId

    def getURL(self, autoConvertToLocal=True) -> str:
        _, cloudURL = self.__getCheckedCloud(autoConvertToLocal)
        return cloudURL

    def __str__(self):
        converted = '{}'.format(', convertedToLocal' if cloudMemeNeedsToBeConvertedToLocal(self.cloudURL) else '')
        return f'Meme(id={self.id}, name="{self.name}", {self.mediaType}, ext="{self.fileExt}", tags={self.tags}, cloudId={self.getCloudID()}, url={self.getURL()}{converted})'