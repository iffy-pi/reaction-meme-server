import os
import csv

import requests

from apiutils.MemeManagement.MemeDBInterface import MemeDBInterface, MemeDBException
from apiutils.MemeManagement.MemeContainer import MemeContainer
from apiutils.MemeManagement.MemeMediaType import getMediaTypeForExt, MemeMediaType
from apiutils.MemeManagement.MemeLibrarySearcher import MemeLibrarySearcher, MemeSearchHit
from apiutils.MemeManagement.MemeStorageInterface import MemeStorageInterface
from apiutils.ThumbnailMaker import ThumbnailMaker


class MemeLibraryException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MemeLibrary:
    def __init__(self, db:MemeDBInterface, mediaStorage:MemeStorageInterface):
        """
        Class to manage database of reaction memes, will handle the loading, reading and writing of the JSON db file
        """
        self.db = db
        self.libSearcher = MemeLibrarySearcher()
        self.mediaStorage = mediaStorage

    def hasMeme(self, itemId:int):
        return self.db.hasMeme(itemId)

    def getMeme(self, itemId:int):
        if not self.hasMeme(itemId):
            raise MemeLibraryException("Item ID does not exist in db")
        return self.db.getMeme(itemId)

    def uploadMemeMedia(self, itemId:int, mediaBinary: bytes) -> str:
        """
        Uploads the media binary to the cloud and associates it with the item pointed to by the item ID
        :param itemId: The id of the item in the database
        :param mediaBinary: The bytes of the media to be uploaded
        :return: The media URL, None if the operation was not completed successfully
        """
        cloudId, cloudURL = self.mediaStorage.uploadMedia(mediaBinary, self.getMeme(itemId).getFileExt())

        if cloudId is None or cloudURL is None:
            return None

        if not self.db.updateMeme(itemId, MemeContainer(mediaID=cloudId, mediaURL=cloudURL)):
            return None

        return cloudURL

    def uploadMedia(self, mediaBinary:bytes, fileExt:str) -> tuple[str, str]:
        mediaID, mediaURL = self.mediaStorage.uploadMedia(mediaBinary, fileExt)
        return mediaID, mediaURL

    def __makeB64Thumbnail(self, mediaID:str, mediaType:MemeMediaType) -> str:
        imgBytes = None
        if mediaType == MemeMediaType.IMAGE:
            imgBytes = self.mediaStorage.getMedia(mediaID)

        elif mediaType == MemeMediaType.VIDEO:
            imgBytes = self.mediaStorage.videoToThumbnail(mediaID)

        else:
            raise Exception('Unknown media type for conversion')

        # now create thumbnail
        thumbnailB64 = ThumbnailMaker.makeBase64Thumbnail(imgBytes)
        return thumbnailB64

    def addMemeToLibrary(self, name=None, fileExt=None, tags=None, mediaID=None, mediaURL=None, addMemeToIndex:bool=False) -> MemeContainer:
        """
        Creates a new item in the database with the available fields
        Returns a MemeLibraryItem if operation was successful else None
        Note: This makes changes to the database loaded in memory, save/write the Library to push the changes to the remote database
        """
        fileExt = fileExt.lower().replace('.', '')
        mediaType = getMediaTypeForExt(fileExt)
        meme = MemeContainer(id=None, name=name, mediaType=mediaType, fileExt=fileExt, tags=tags, mediaID=mediaID, mediaURL=mediaURL)

        if fileExt is not None and mediaID is not None:
            th = None
            try:
                th = self.__makeB64Thumbnail(mediaID, mediaType)
            except Exception as e:
                raise MemeLibraryException(f'Could not make thumbnail: {e}')

            meme.setProperty(thumbnail=th)

        if not self.db.addMemeToDB(meme):
            return None

        if addMemeToIndex and not self.libSearcher.hasIndex():
            self.indexMeme(meme)
        return meme

    def addAndUploadMeme(self, mediaBinary:bytes, name:str, fileExt:str, tags:list[str], addMemeToIndex:bool=False) -> MemeContainer:
        """
        Uploads the mediaBinary to the configured meme media storage and configures a new entry in the database
        Note: This makes changes to the database loaded in memory, save/write the Library to push the changes to the remote database
        """
        # upload the media
        fileExt = fileExt.lower().replace('.', '')
        mediaID, mediaURL = self.mediaStorage.uploadMedia(mediaBinary, fileExt)

        if mediaID is None or mediaURL is None:
            return None

        # add to library
        return self.addMemeToLibrary(name=name, fileExt=fileExt, tags=tags, mediaID=mediaID, mediaURL=mediaURL, addMemeToIndex=addMemeToIndex)

    def addAndUploadMemeFrom(self, filePath, name, tags, addMemeToIndex=False) -> MemeContainer:
        """
        Uploads the file from filepath to the configured meme media storage and configures a new entry in the database
        Note: This makes changes to the database loaded in memory, save/write the Library to push the changes to the remote database
        """
        # first upload the file to cloudinary
        with open(filePath, 'rb') as file:
            mediaBinary = file.read()
        return self.addAndUploadMeme(mediaBinary, name, os.path.splitext(filePath)[1].replace('.', ''), tags, addMemeToIndex=addMemeToIndex)


    def editMeme(self, itemId:int, name: str = None, tags:list[str] = None) -> bool:
        """
        Edits a meme in the database, allows you to edit the name or tags of the meme
        Note: This makes changes to the database loaded in memory, save/write the Library to push the changes to the remote database
        Returns true if the operation was completed
        """
        if not self.hasMeme(itemId):
            raise MemeLibraryException(f'ID "{itemId}" does not exist in database')

        return self.db.updateMeme(itemId, MemeContainer(name=name, tags=tags))

    def addMemeThumbnail(self, memeID:int):
        """
        Creates the base64 encoded thumbnail and adds it to the database for the meme with the given memeID
        """
        if not self.hasMeme(memeID):
            raise MemeLibraryException(f'ID "{memeID}" does not exist in database')

        meme = self.getMeme(memeID)
        mediaID = meme.getMediaID()
        mediaType = meme.getMediaType()

        if mediaID is None:
            raise MemeLibraryException('No Cloud ID is available for meme')

        th = None
        try:
            th = self.__makeB64Thumbnail(mediaID, mediaType)
        except Exception as e:
            raise MemeLibraryException(f'Could not make thumbnail: {e}')

        meme.setProperty(thumbnail=th)
        return self.db.updateMeme(memeID, meme)

    def makeLibraryFromCSV(self, csvFile):
        """
        Reads the CSV file and creates the library from the data in the CSV file. The CSV file should be structured such that:
            - CSV file is in UTF-8
            - There is a header row
            - Columns are <CloudID>,<Cloud URL>,<Name>,<File Ext>,<Tags>
            - Tags are comma-separated strings e.g. "blue,ball,big"
        CSV file reading is stopped if one or more columns in a row is empty
        """

        # reset database to empty state
        self.db.initDB()

        #catalogFile = os.path.join(PROJECT_ROOT, 'data', 'catalog.csv')

        # read elements from the catalog and add to it
        with (open(csvFile, 'r', encoding='utf-8') as file):
            table = csv.reader(file, delimiter=',')
            for i, row in enumerate(table):
                if i == 0:
                    continue

                cloudId = row[0].lower().strip()
                cloudURL = row[1].lower().strip()
                name = row[2].strip().lower()
                fileExt = row[3].strip().lower().replace('.', '')
                tags = row[4].strip().lower()

                if any(t == '' for t in (cloudId, cloudURL, name, fileExt)):
                    break

                tags = [ e.strip() for e in tags.split(',')]
                mediaType = getMediaTypeForExt(fileExt)
                self.db.addMemeToDB(MemeContainer(None, name, mediaType, fileExt, tags, cloudId, cloudURL))

    def indexLibrary(self):
        """
        Indexes all the memes in the library, if index already exists, it is re-indexed
        """
        self.libSearcher.indexMemeList(self.db.getAllDBMemes())

    def indexMeme(self, meme:MemeContainer):
        """
        Adds the given meme to the library index, if index is not present, then the library is indexed again
        """
        if not self.libSearcher.hasIndex():
            self.indexLibrary()

        self.libSearcher.indexMeme(meme)

    def search(self, query:str, itemsPerPage:int=10, pageNo:int=1, onlyMediaType:MemeMediaType=None, excludeMediaType: MemeMediaType = None) -> list[MemeContainer]:
        """
        Get the memes that match the search query
        :param query: The search query
        :param itemsPerPage: The number of items per page of search results
        :param pageNo: The page in search results
        :param excludeMediaType: Exclude this meme media type from the search results
        :param onlyMediaType: Search results should only be of this meme media type
        :return: The list of meme URLs
        """
        results = self.libSearcher.search(query, itemsPerPage, pageNo, onlyMediaType=onlyMediaType, excludeMediaType=excludeMediaType)
        return [ self.getMeme(hit.memeID) for hit in results]

    def browseMemes(self, itemsPerPage:int, pageNo:int) -> list[MemeContainer]:
        """
        Browse the repository of memes
        :param itemsPerPage: The number of items per page of search results
        :param pageNo: The page in search results
        """
        return self.db.getGroupOfMemes(itemsPerPage, pageNo)

    def saveLibrary(self) -> bool:
        """
        Saves the contents of the library to the database
        Returns true if the operation was completed successfully
        """
        return self.db.writeDB()

    def loadLibrary(self) -> bool:
        """
        Loads the library from the database
        Returns true if the operation was completed successfully
        """
        return self.db.loadDB()