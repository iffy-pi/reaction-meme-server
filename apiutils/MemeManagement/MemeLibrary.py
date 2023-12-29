import os
import csv

from apiutils.MemeManagement.MemeDBInterface import MemeDBInterface, MemeDBException
from apiutils.MemeManagement.MemeLibraryItem import MemeLibraryItem
from apiutils.MemeManagement.MemeMediaType import getMediaTypeForExt
from apiutils.MemeManagement.MemeLibrarySearcher import MemeLibrarySearcher
from apiutils.MemeManagement.MemeUploaderInterface import MemeUploaderInterface

class MemeLibraryException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MemeLibrary:
    def __init__(self, db:MemeDBInterface, uploader:MemeUploaderInterface):
        """
        Class to manage database of reaction memes, will handle the loading, reading and writing of the JSON db file
        """
        self.db = db
        self.libSearcher = MemeLibrarySearcher()
        self.uploader = uploader

    def hasMeme(self, itemId:int):
        return self.db.hasItem(itemId)

    def getMeme(self, itemId:int):
        if not self.hasMeme(itemId):
            raise MemeLibraryException("Item ID does not exist in db")
        return self.db.getMemeItem(itemId)

    def uploadItemMedia(self, itemId:int, mediaBinary):
        """
        Uploads the media binary to the cloud and associates it with the item pointed to by the item ID
        :param itemId: The id of the item in the database
        :param mediaBinary: The binary data of the media to be uploaded
        :return: The cloud URL
        """
        cloudId, cloudURL = self.uploader.uploadMedia(mediaBinary, self.getMeme(itemId).getFileExt())
        self.db.updateItem(itemId, MemeLibraryItem(cloudID=cloudId, cloudURL=cloudURL))

        return cloudURL

    def addMemeToLibrary(self, name=None, fileExt=None, tags=None, cloudID=None, cloudURL=None, addMemeToIndex:bool=False) -> MemeLibraryItem|None:
        """
        Creates a new item in the database with the available fields
        Returns a MemeLibraryItem if operation was successful else None
        Note: This makes changes to the database loaded in memory, save/write the Library to push the changes to the remote database
        """
        fileExt = fileExt.lower().replace('.', '')
        meme = MemeLibraryItem(id=None, name=name, type=getMediaTypeForExt(fileExt), fileExt=fileExt, tags=tags, cloudID=cloudID, cloudURL=cloudURL)

        if not self.db.addMemeToDB(meme):
            return None

        if addMemeToIndex and not self.libSearcher.hasIndex():
            self.indexMeme(meme)
        return meme

    def addAndUploadMeme(self, mediaBinary:bytes, name:str, fileExt:str, tags:list[str], addMemeToIndex:bool=False) -> MemeLibraryItem|None:
        """
        Uploads the mediaBinary to the configured meme media storage and configures a new entry in the database
        Note: This makes changes to the database loaded in memory, save/write the Library to push the changes to the remote database
        """
        # upload the media
        fileExt = fileExt.lower().replace('.', '')
        cloudId, cloudURL = self.uploader.uploadMedia(mediaBinary, fileExt)
        # add to library
        return self.addMemeToLibrary(name=name, fileExt=fileExt, tags=tags, cloudID=cloudId, cloudURL=cloudURL, addMemeToIndex=addMemeToIndex)

    def addAndUploadMemeFrom(self, filePath, name, tags, addMemeToIndex=False) -> MemeLibraryItem|None:
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

        return self.db.updateItem(itemId, MemeLibraryItem(name=name, tags=tags))


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
                self.db.addMemeToDB(MemeLibraryItem(None, name, mediaType, fileExt, tags, cloudId, cloudURL))

    def indexLibrary(self):
        """
        Indexes all the memes in the library, if index already exists, it is re-indexed
        """
        self.libSearcher.indexMemeList(self.db.getAllDBMemes())

    def indexMeme(self, meme:MemeLibraryItem):
        """
        Adds the given meme to the library index, if index is not present, then the library is indexed again
        """
        if not self.libSearcher.hasIndex():
            self.indexLibrary()

        self.libSearcher.indexMeme(meme)


    def findMemeURLs(self, query:str, itemsPerPage:int=10, pageNo:int=1) -> list[str]:
        """
        Get the URLs of memes which match the given search query
        :param query: The search query
        :param itemsPerPage: The number of items per page of search results
        :param pageNo: The page in search results
        :return: The list of meme URLs
        """
        return [self.libSearcher.getSearchResultAttr(res, memeURL=True) for res in self.libSearcher.search(query, itemsPerPage, pageNo)]

    def findMemes(self, query:str, itemsPerPage:int=10, pageNo:int=1) -> list[MemeLibraryItem]:
        """
        Get the memes that match the search query
        :param query: The search query
        :param itemsPerPage: The number of items per page of search results
        :param pageNo: The page in search results
        :return: The list of meme URLs
        """
        results = self.libSearcher.search(query, itemsPerPage, pageNo)
        ids = [ self.libSearcher.getSearchResultAttr(res, memeID=True) for res in results ]
        return [ self.getMeme(memeId) for memeId in ids ]

    def browseMemes(self, itemsPerPage:int, pageNo:int) -> list[MemeLibraryItem]:
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