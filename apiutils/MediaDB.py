import os
import uuid
import csv
from contextlib import contextmanager

import cloudinary
import cloudinary.uploader
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, STORED
from whoosh import index
from whoosh.qparser import OrGroup, MultifieldParser

from apiutils.FileServers.MediaDBFileServer import MediaDBFileServer
from apiutils.configs.config import PROJECT_ROOT


class MediaDB:
    class DBFields:
        ItemCount = "itemCount"
        Items = "items"
        class ItemFields:
            ID = 'id'
            Name = "name"
            FileExt = "fileExt"
            Tags = "tags"
            CloudID = "cloudID"
            CloudURL = "cloudURL"

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
            return MultifieldParser([MediaDB.IndexingManager.SchemaFields.Name, MediaDB.IndexingManager.SchemaFields.Tags],
                                    schema=schemaIn,
                                    group=OrGroup)

        @staticmethod
        def addItemToWriter(indexWriter, item):
            """
            Adds the dbElement to the index written to by indexWriter
            :param indexWriter: An instance of whoosh.index.writer()
            :param item: An object of db, containing fields from MediaDB.DBFields.ElementFields
            """
            indexWriter.add_document(fileID=item[MediaDB.DBFields.ItemFields.ID],
                                     name=item[MediaDB.DBFields.ItemFields.Name],
                                     tags=','.join(item[MediaDB.DBFields.ItemFields.Tags]))

    # TODO: Make singleton class!
    # TODO: Decouple db controller from MediaDB? (all this schema stuff should move)
    def __init__(self, fileServer:MediaDBFileServer, dbIndex=None, testing=True):
        """
        Class to manage database of reaction memes, will handle the loading, reading and writing of the JSON db file
        """
        self.db = None
        self.__fileServer = fileServer
        self.testing = testing


        self.dbSchema = MediaDB.IndexingManager.createDBSchema()
        self.searchQueryParser = MediaDB.IndexingManager.createQueryParser(self.dbSchema)

        self.dbIndex = None
        self.dbIndexDir = os.path.join(PROJECT_ROOT, 'data', 'indexdir')

        # Configure cloudinary
        # cloudinary.configs(
        #     cloud_name = CLOUD_NAME,
        #     api_key = API_KEY,
        #     api_secret = API_SECRET,
        # )

    def __del__(self):
        # Writes the json file away
        pass

    def initDB(self):
        self.db = {
            MediaDB.DBFields.ItemCount: 0,
            MediaDB.DBFields.Items: {}
        }

    def loadDB(self):
        self.db = self.__fileServer.loadDBFromJSON()

    def saveDBChanges(self):
        self.__fileServer.writeJSONDB(self.db)

    def __addItemToDB(self, name, fileExt, tags, cloudID, cloudURL):
        itemId = str(self.db[MediaDB.DBFields.ItemCount])

        self.db[MediaDB.DBFields.Items][itemId] = {
            MediaDB.DBFields.ItemFields.ID           : itemId,
            MediaDB.DBFields.ItemFields.Name         : name,
            MediaDB.DBFields.ItemFields.FileExt      : fileExt,
            MediaDB.DBFields.ItemFields.Tags         : tags,
            MediaDB.DBFields.ItemFields.CloudID      : cloudID,
            MediaDB.DBFields.ItemFields.CloudURL     : cloudURL
        }
        self.db[MediaDB.DBFields.ItemCount] += 1
        return itemId

    def __getPropertyForItem(self, itemID:str, propField):
        """
        Gets the element property for the given ID
        :param propField: The element property to retrieve
        :param itemID: The DB id for the media
        :return: The cloudinary URL
        """
        return self.getItem(itemID).get(propField)

    def __updatePropertyForItem(self, itemID:str, propField, propValue):
        self.getItem(itemID)[propField] = propValue

    def hasItem(self, itemID):
        return str(itemID) in self.db[MediaDB.DBFields.Items]

    def getItem(self, itemID):
        """
        Returns the db item for the given item ID
        :param itemID:
        :return: the database item
        """
        itemID = str(itemID)
        if not self.hasItem(itemID):
            raise Exception(f'Element ID: "{itemID}" not in database')

        return self.db.get(MediaDB.DBFields.Items).get(itemID)

    def createNewItem(self, name='', fileExt='', tags='', cloudID='', cloudURL=''):
        """
        Creates a new item in the database with the available fields
        :return: The item ID in the database
        """
        return self.__addItemToDB(name, fileExt, tags, cloudID, cloudURL)

    def __mockUploader(self, mediaBinary, fileExt):

        def filePathToLink(fp):
            # replace backslashes with forward slashes
            return "file:///{}".format(fp.replace('\\', '/'))

        # saves them to local location
        mockLocation = os.path.join(PROJECT_ROOT, 'data', 'mock_cloud')
        fileId = str(uuid.uuid4())
        filePath = os.path.join(mockLocation, f'{fileId}.{fileExt}')
        with open( filePath, 'wb') as file:
            file.write(mediaBinary)

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

    def uploadItemMedia(self, itemId, mediaBinary):
        """
        Uploads the media binary to the cloud and associates it with the item pointed to by the item ID
        :param itemId: The id of the item in the database
        :param mediaBinary: The binary data of the media to be uploaded
        :return: The cloud URL
        """
        cloudId, cloudURL = self.uploadMediaToCloud(mediaBinary, self.getItemFileExt(itemId))
        self.updateItemProperty(itemId, cloudID=cloudId, cloudURL=cloudURL)
        return cloudURL

    def addMedia(self, mediaBinary, name, fileExt, tags, reIndexDB=False):
        # upload to cloudinary
        cloudId, cloudURL = self.uploadMediaToCloud(mediaBinary, fileExt)

        # add to DB
        itemId = self.__addItemToDB(name, fileExt, tags, cloudId, cloudURL)

        # add item to index if requested
        if reIndexDB and self.dbIndex is not None:
            writer = self.dbIndex.writer()
            MediaDB.IndexingManager.addItemToWriter(writer, self.getItem(itemId))
            writer.commit()

    def addMediaFrom(self, filePath, name, tags, reIndexDB=False):
        # first upload the file to cloudinary
        with open(filePath, 'rb') as file:
            mediaBinary = file.read()
        self.addMedia(mediaBinary, name, os.path.splitext(filePath)[1].replace('.', ''), tags, reIndexDB=reIndexDB)

    def initDBToCatalog(self):
        """
        Reads the catalog csv and writes the elements into the DB
        :return:
        """

        # reset database to empty state
        self.initDB()

        catalogFile = os.path.join(PROJECT_ROOT, 'data', 'catalog.csv')
        memeLocation = "C:\\Users\\omnic\\local\\reaction-memes"

        "file:///C:/Users/omnic/local/reaction-memes/meme_2.jpg"

        def filePathToLink(fp):
            # replace backslashes with forward slashes
            return "file:///{}".format(fp.replace('\\', '/'))


        # read elements from the catalog and add to it
        with open(catalogFile, 'r', encoding='utf-8') as file:
            table = csv.reader(file, delimiter=',')
            for i, row in enumerate(table):
                if i == 0:
                    continue
                if row[1].strip() == '':
                    break

                name = row[1].strip()
                fileExt = row[2].strip()
                tags = [ e.strip() for e in row[3].split(',')]
                cloudId = row[0]
                cloudURL = filePathToLink(os.path.join(memeLocation, f'meme_{cloudId}.{fileExt}'))

                self.__addItemToDB(name, fileExt, tags, cloudId, cloudURL)

        # write the db
        self.saveDBChanges()

    def indexDB(self):
        """
        Indexes the media elements in our JSON db for whoosh to implement our searching
        :return:
        """
        if self.db is None:
            self.loadDB()

        if not os.path.exists(self.dbIndexDir):
            os.makedirs(self.dbIndexDir)

        # Creates a fresh index
        self.dbIndex = index.create_in(self.dbIndexDir, self.dbSchema)

        # open the writer to add documents to the index
        writer = self.dbIndex.writer()
        for item in self.db[MediaDB.DBFields.Items].values():
            MediaDB.IndexingManager.addItemToWriter(writer, item)
        writer.commit()

    @contextmanager
    def getDBSearcher(self):
        if self.dbIndex is None:
            raise Exception('Database has not been indexed')

        searcher = self.dbIndex.searcher()
        try:
            yield searcher
        finally:
            searcher.close()

    def findItemIDsFor(self, query:str, limit:int = 15):
        """
        Searches the indexed database with whoosh.
        Returns the list of Ids that match the query
        :return:
        """
        q = self.searchQueryParser.parse(query)
        with self.getDBSearcher() as s:
            results = s.search(q)
            return [ r[MediaDB.IndexingManager.SchemaFields.FileID] for r in results ]

    def findItemURLsFor(self, query:str, limit:int=25):
        res = self.findItemIDsFor(query, limit=limit)
        return [self.getItemURL(itemId) for itemId in res]

    def getItemName(self, itemId):
        return self.__getPropertyForItem(itemId, MediaDB.DBFields.ItemFields.Name)

    def getItemTags(self, itemId):
        return self.__getPropertyForItem(itemId, MediaDB.DBFields.ItemFields.Tags)

    def getItemFileExt(self, itemId):
        return self.__getPropertyForItem(itemId, MediaDB.DBFields.ItemFields.FileExt)

    def getItemCloudID(self, itemId):
        return self.__getPropertyForItem(itemId, MediaDB.DBFields.ItemFields.CloudID)

    def getItemURL(self, itemId):
        return self.__getPropertyForItem(itemId, MediaDB.DBFields.ItemFields.CloudURL)


    def updateItemProperty(self, itemId, name:str=None, tags:list[str]=None, fileExt=None, cloudID=None, cloudURL=None ):
        item = self.getItem(itemId)
        if name is not None:
            item[MediaDB.DBFields.ItemFields.Name] = name
        if tags is not None:
            item[MediaDB.DBFields.ItemFields.Tags] = tags
        if fileExt is not None:
            item[MediaDB.DBFields.ItemFields.FileExt] = fileExt
        if cloudID is not None:
            item[MediaDB.DBFields.ItemFields.CloudID] = cloudID
        if cloudURL is not None:
            item[MediaDB.DBFields.ItemFields.CloudURL] = cloudURL







