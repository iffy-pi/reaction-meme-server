import os
import time
import uuid
import csv
from contextlib import contextmanager

import cloudinary
import cloudinary.uploader
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, STORED
from whoosh import index
from whoosh.qparser import OrGroup, MultifieldParser
from whoosh.filedb.filestore import RamStorage

from apiutils.configs.config import PROJECT_ROOT
from apiutils.DBClasses.MediaDB import MediaDB
from apiutils.MemeManagement.MemeLibraryItem import MemeLibraryItem

class MemeLibrary:
    instance = None
    class IndexingManager:
        # Manages everything to do with the schemas used when indexing the db
        # Including the fields, creating the schema, adding items to an index, creating the parser
        class SchemaFields:
            """
            The field names used in the schema, see DBSchemaManager.createDBSchema() for their properties
            """
            FileID = "fileID"
            Name = "name"
            Tags = "tags"


        @staticmethod
        def createDBSchema():
            """
            Creates the whoosh schema for the DB with the indexable fields configured
            :return: The created
            """
            # indexing schema, searchable by the file name and its comma separated tags (see SchemaFields)
            # fileID and name is stored so it is returned with results
            return Schema(fileID=STORED,
                          name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                          tags=KEYWORD(lowercase=True, scorable=True, commas=True, analyzer=StemmingAnalyzer()))

        @staticmethod
        def createQueryParser(schemaIn):
            """
            Creates the query parser for the db. Parser is configured to use the fields in the schema returned from DBSchemaManager.createDBSchema()
            :return: The created parser
            """
            # Designed to search in both names and tag field, using an or-ing of results
            return MultifieldParser([MemeLibrary.IndexingManager.SchemaFields.Name, MemeLibrary.IndexingManager.SchemaFields.Tags],
                                    schema=schemaIn,
                                    group=OrGroup)

        @staticmethod
        def addMemeToWriter(indexWriter, item:MemeLibraryItem):
            """
            Adds the dbElement to the index written to by indexWriter
            :param indexWriter: An instance of whoosh.index.writer()
            :param item: An object of db, containing fields from MediaDB.DBFields.ElementFields
            """
            indexWriter.add_document(fileID=item.getID(),
                                     name=item.getName(),
                                     tags=','.join(item.getTags()))

    def __init__(self, db:MediaDB, testing):
        """
        Class to manage database of reaction memes, will handle the loading, reading and writing of the JSON db file
        """
        self.db = db
        self.testing = testing

        self.dbSchema = MemeLibrary.IndexingManager.createDBSchema()
        self.searchQueryParser = MemeLibrary.IndexingManager.createQueryParser(self.dbSchema)

        self.dbIndex = None
        self.dbIndexDir = os.path.join(PROJECT_ROOT, 'data', 'indexdir')
        self.__indexStorage = RamStorage()
        self.__indexLock = False

        # Configure cloudinary
        # cloudinary.configs(
        #     cloud_name = CLOUD_NAME,
        #     api_key = API_KEY,
        #     api_secret = API_SECRET,
        # )

    @staticmethod
    def initSingleton(db:MediaDB, testing=True):
        MemeLibrary.instance = MemeLibrary(db, testing)

    @staticmethod
    def getSingleton():
        if MemeLibrary.instance is None:
            raise Exception('Uinitialized library!')
        return MemeLibrary.instance

    def hasMeme(self, itemId:int):
        return self.db.hasItem(itemId)

    def getMeme(self, itemId:int):
        if not self.hasMeme(itemId):
            raise Exception("Item ID does not exist in db")
        return self.db.getMemeItem(itemId)

    def __mockUploader(self, mediaBinary, fileExt):

        def filePathToLink(fp):
            # replace backslashes with forward slashes
            return "file:///{}".format(fp.replace('\\', '/'))

        # saves them to local location
        mockLocation = os.path.join('data', 'mock_cloud')
        fileId = str(uuid.uuid4())
        filePath = os.path.join(mockLocation, f'{fileId}.{fileExt}')
        # with open( filePath, 'wb') as file:
        #     file.write(mediaBinary)
        return fileId, filePathToLink(filePath)

    def __realUploader(self, mediaBinary):
        # Actually uploads the files to cloudinary
        resp = cloudinary.uploader.upload(mediaBinary, unique_filename=False, overwrite=True)
        mediaID = resp['public_id']
        deliveryURL = cloudinary.CloudinaryImage(mediaID).build_url()
        return mediaID, deliveryURL

    def uploadMediaToCloud(self, mediaBinary, fileExt):
        """
        Uploads the binary to cloudinary and returns the URL for delivery
        """
        if self.testing:
            return self.__mockUploader(mediaBinary, fileExt)
        else:
            return self.__realUploader(mediaBinary)

    def uploadItemMedia(self, itemId:int, mediaBinary):
        """
        Uploads the media binary to the cloud and associates it with the item pointed to by the item ID
        :param itemId: The id of the item in the database
        :param mediaBinary: The binary data of the media to be uploaded
        :return: The cloud URL
        """
        cloudId, cloudURL = self.uploadMediaToCloud(mediaBinary, self.getMeme(itemId).getFileExt())

        self.db.updateItem(itemId, MemeLibraryItem(cloudID=cloudId, cloudURL=cloudURL))

        return cloudURL

    def makeMemeAndAddToLibrary(self, name=None, fileExt=None, tags=None, cloudID=None, cloudURL=None, reIndexLibrary:bool=False) -> MemeLibraryItem:
        """
        Creates a new item in the database with the available fields
        :return: The item ID in the database
        """
        meme = MemeLibraryItem(id=None, name=name, fileExt=fileExt, tags=tags, cloudID=cloudID, cloudURL=cloudURL)

        self.db.addMemeToDB(meme)

        if reIndexLibrary and self.dbIndex is not None:
            self.indexMeme(meme)
        return meme

    def addAndUploadMeme(self, mediaBinary, name:str, fileExt:str, tags:list[str], reIndexLibrary:bool=False):
        # upload to cloudinary
        cloudId, cloudURL = self.uploadMediaToCloud(mediaBinary, fileExt)
        # add to library
        meme = self.makeMemeAndAddToLibrary(name=name, fileExt=fileExt, tags=tags, cloudID=cloudId, cloudURL=cloudURL, reIndexLibrary=reIndexLibrary)

    def addAndUploadMemeFrom(self, filePath, name, tags, reIndexLibrary=False):
        # first upload the file to cloudinary
        with open(filePath, 'rb') as file:
            mediaBinary = file.read()
        self.addAndUploadMeme(mediaBinary, name, os.path.splitext(filePath)[1].replace('.', ''), tags, reIndexLibrary=reIndexLibrary)

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
                fileExt = row[3].strip().lower()
                tags = row[4].strip().lower()

                if any(t == '' for t in (cloudId, cloudURL, name, fileExt, tags)):
                    break

                tags = [ e.strip() for e in tags.split(',')]

                self.db.addMemeToDB(MemeLibraryItem(None, name, fileExt, tags, cloudId, cloudURL))

        # write the db
        # self.db.writeDB()

    # TODO: Is our mutex/semaphore lock stuff configured correctly, ELEC 377 review
    # TODO: Do DB locks in db class
    def isIndexLocked(self):
        return self.__indexLock

    def getIndexLock(self):
        # wait till index unlocks
        while self.isIndexLocked():
            pass

        self.__indexLock = True

    def releaseIndexLock(self):
        self.__indexLock = False


    def indexLibrary(self):
        """
        Indexes all the memes in the library, if index already exists, it is re-indexed
        :return:
        """
        self.getIndexLock()

        # Creates a fresh index
        self.dbIndex = self.__indexStorage.create_index(self.dbSchema)

        # open the writer to add documents to the index
        writer = self.dbIndex.writer()
        for item in self.db.getAllDBMemes():
            MemeLibrary.IndexingManager.addMemeToWriter(writer, item)
        writer.commit()

        # release the lock
        self.releaseIndexLock()

    def indexMeme(self, meme:MemeLibraryItem):
        """
        Adds the given meme to the library index, if index is not present, then the library is indexed again
        """
        if self.dbIndex is None:
            self.indexLibrary()

        self.getIndexLock()
        writer = self.dbIndex.writer()
        MemeLibrary.IndexingManager.addMemeToWriter(writer, meme)
        writer.commit()
        self.releaseIndexLock()

    @contextmanager
    def getDBSearcher(self):
        if self.dbIndex is None:
            raise Exception('Database has not been indexed')

        self.getIndexLock()
        searcher = self.dbIndex.searcher()
        try:
            yield searcher
        finally:
            searcher.close()
            self.releaseIndexLock()

    def __findMemeIDs(self, query:str, limit:int = 15):
        """
        Searches the indexed database with whoosh.
        Returns the list of Ids that match the query
        :return:
        """
        q = self.searchQueryParser.parse(query)
        with self.getDBSearcher() as s:
            results = s.search(q)
            return [r[MemeLibrary.IndexingManager.SchemaFields.FileID] for r in results]

    def findMemesFor(self, query:str, limit:int = 15):
        ids = self.__findMemeIDs(query, limit=limit)
        return [ self.getMeme(memeId) for memeId in ids ]

    def saveLibrary(self):
        self.db.writeDB()

    def loadLibrary(self):
        self.db.loadDB()