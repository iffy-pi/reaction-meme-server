from apiutils.MemeManagement.MemeMediaType import MemeMediaType, memeMediaTypeToString, memeMediaTypeToInt, \
    stringToMemeMediaType
from localMemeStorageServer.utils.LocalStorageUtils import cloudMemeNeedsToBeConvertedToLocal, getLocalVersionForCloudMeme
class MemeContainer:
    """
    Class used as a data container for meme information. It is not connected to the meme library or the meme database that created it.
    """
    def __init__(self, id:int=None, name:str=None, mediaType: MemeMediaType =None, fileExt=None, tags:list[str]=None, mediaID=None, mediaURL=None, mediaTypeStr:str=None, thumbnail:str=None):
        self.id = id
        self.name =     name
        self.tags =     tags
        self.fileExt =  fileExt
        self.mediaID =  mediaID
        self.mediaURL = mediaURL
        self.mediaType = None
        self.thumbnail = thumbnail

        if mediaTypeStr is not None:
            self.mediaType = stringToMemeMediaType(mediaTypeStr)

        if mediaType is not None:
            self.mediaType = mediaType

    @staticmethod
    def makeEmptyMeme():
        return MemeContainer(
            name='',
            mediaType=MemeMediaType.UNKNOWN,
            fileExt='',
            tags=[],
            mediaID='',
            mediaURL='',
            thumbnail=''
        )

    def setProperty(self, id:int=None, name:str=None, mediaType:MemeMediaType =None, fileExt:str=None, tags:list[str]=None, mediaID:str=None, mediaURL:str=None, thumbnail:str=None):
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
        if mediaID is not None:
            self.mediaID = mediaID
        if mediaURL is not None:
            self.mediaURL = mediaURL
        if mediaType is not None:
            self.mediaType = mediaType
        if thumbnail is not None:
            self.thumbnail = thumbnail

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

    def getThumbnail(self) -> str:
        return self.thumbnail

    def __getCheckedCloud(self, autoConvertToLocal:bool) -> tuple[str, str]:
        if not (autoConvertToLocal and cloudMemeNeedsToBeConvertedToLocal(self.mediaURL)):
            return self.mediaID, self.mediaURL
        return getLocalVersionForCloudMeme(self.mediaID, self.mediaURL, self.fileExt)

    def getMediaID(self, autoConvertToLocal=True) -> str:
        mediaId, _ = self.__getCheckedCloud(autoConvertToLocal)
        return mediaId

    def getMediaURL(self, autoConvertToLocal=True) -> str:
        _, mediaURL = self.__getCheckedCloud(autoConvertToLocal)
        return mediaURL

    def __str__(self):
        converted = '{}'.format(', convertedToLocal' if cloudMemeNeedsToBeConvertedToLocal(self.mediaURL) else '')
        thStr = '...' if self.thumbnail is not None else ''
        return f'Meme(id={self.id}, name="{self.name}", {self.mediaType}, ext="{self.fileExt}", tags={self.tags}, cloudId={self.getMediaID()}, url={self.getMediaURL()}{converted}, thumbnail="{thStr}")'