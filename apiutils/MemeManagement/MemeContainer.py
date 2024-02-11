from apiutils.MemeManagement.MemeMediaType import MemeMediaType, memeMediaTypeToString, memeMediaTypeToInt, \
    stringToMemeMediaType
from localMemeStorageServer.utils.LocalStorageUtils import cloudMemeNeedsToBeConvertedToLocal, getLocalVersionForCloudMeme
class MemeContainer:
    """
    Class used as a data container for meme information. It is not connected to the meme library or the meme database that created it.
    """
    def __init__(self, id:int=None, name:str=None, mediaType: MemeMediaType =None, fileExt=None, tags:list[str]=None, mediaID=None, mediaURL=None, mediaTypeStr:str=None, thumbnail:str=None):
        self.__id = id
        self.__name =     name
        self.__tags =     tags
        self.__fileExt =  fileExt
        self.__mediaID =  mediaID
        self.__mediaURL = mediaURL
        self.__mediaType = None
        self.__thumbnail = thumbnail

        if mediaTypeStr is not None:
            self.__mediaType = stringToMemeMediaType(mediaTypeStr)

        if mediaType is not None:
            self.__mediaType = mediaType

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
            self.__id = id
        if name is not None:
            self.__name = name
        if fileExt is not None:
            self.__fileExt = fileExt
        if tags is not None:
            self.__tags = tags
        if mediaID is not None:
            self.__mediaID = mediaID
        if mediaURL is not None:
            self.__mediaURL = mediaURL
        if mediaType is not None:
            self.__mediaType = mediaType
        if thumbnail is not None:
            self.__thumbnail = thumbnail

    def getID(self) -> int:
        return self.__id

    def getName(self) -> str:
        return self.__name

    def getTags(self) -> list[str]:
        return self.__tags

    def getMediaType(self) -> MemeMediaType:
        return self.__mediaType

    def getMediaTypeString(self) -> str:
        if self.__mediaType is None:
            return None
        return memeMediaTypeToString(self.__mediaType)

    def getMediaTypeInt(self) -> int:
        if self.__mediaType is None:
            return None
        return memeMediaTypeToInt(self.__mediaType)

    def getFileExt(self) -> str:
        return self.__fileExt

    def getThumbnail(self) -> str:
        return self.__thumbnail

    def __getCheckedCloud(self, autoConvertToLocal:bool) -> tuple[str, str]:
        if not (autoConvertToLocal and cloudMemeNeedsToBeConvertedToLocal(self.__mediaURL)):
            return self.__mediaID, self.__mediaURL
        return getLocalVersionForCloudMeme(self.__mediaID, self.__mediaURL, self.__fileExt)

    def getMediaID(self, autoConvertToLocal=True) -> str:
        mediaId, _ = self.__getCheckedCloud(autoConvertToLocal)
        return mediaId

    def getMediaURL(self, autoConvertToLocal=True) -> str:
        _, mediaURL = self.__getCheckedCloud(autoConvertToLocal)
        return mediaURL

    def __str__(self):
        converted = '{}'.format(', convertedToLocal' if cloudMemeNeedsToBeConvertedToLocal(self.__mediaURL) else '')
        thStr = '...' if self.__thumbnail is not None else ''
        return f'Meme(id={self.__id}, name="{self.__name}", {self.__mediaType}, ext="{self.__fileExt}", tags={self.__tags}, cloudId={self.getMediaID()}, url={self.getMediaURL()}{converted}, thumbnail="{thStr}")'