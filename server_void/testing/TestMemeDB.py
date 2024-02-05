import json

from apiutils.configs.ServerConfig import ServerConfig
from localMemeStorageServer.utils.LocalStorageUtils import cloudMemeNeedsToBeConvertedToLocal, \
    getLocalVersionForCloudMeme


class TestMemeDB:
    """
    Gets data from the testing DB, is designed to work independent of the code base
    """
    class DBFields:
        ItemCount = "itemCount"
        Items = "items"
        class ItemFields:
            ID = 'id'
            Name = "name"
            MediaType = "mediaType"
            FileExt = "fileExt"
            Tags = "tags"
            Thumbnail = "thumbnail"
            MediaID = "mediaID"
            MediaURL = "mediaURL"

    instance = None
    def __init__(self):
        self.dbpath = ServerConfig.path('data/testing_db.json')
        self.db = None

    @staticmethod
    def getInstance():
        if TestMemeDB.instance is None:
            TestMemeDB.instance = TestMemeDB()
        return TestMemeDB.instance

    def loadDB(self):
        with open(self.dbpath, 'r') as file:
            self.db = json.load(file)

    def writeDB(self):
        with open(self.dbpath, 'w') as file:
            json.dump(self.db, file, indent=4)
    def getItems(self) -> dict:
        return self.db[TestMemeDB.DBFields.Items]

    def inDB(self, itemId):
        if self.db is None:
            raise Exception('Missing database')

        return str(itemId) in self.getItems()

    def getItem(self, itemId: int) -> dict:
        if not self.inDB(itemId):
            return None
        return self.getItems()[str(itemId)]

    def get(self, itemId: int, name=False, mediaType=False, fileExt=False, tags=False, mediaID=False, mediaURL=False, thumbnail=False):
        """
        Gets information about an item in the database
        If multiple keys are set to true, values are returned in a dictionary
        """
        item = self.getItem(itemId)
        if item is None:
            return None

        mediaID = item[TestMemeDB.DBFields.ItemFields.MediaID]
        mediaURL = item[TestMemeDB.DBFields.ItemFields.MediaURL]
        fileExt = item[TestMemeDB.DBFields.ItemFields.FileExt]

        if cloudMemeNeedsToBeConvertedToLocal(item[TestMemeDB.DBFields.ItemFields.MediaURL]):
            mediaID, mediaURL = getLocalVersionForCloudMeme(mediaID, mediaURL, fileExt)

        results = {}
        if name:
            results['name'] = item[TestMemeDB.DBFields.ItemFields.Name]
        if tags:
            results['tags'] = item[TestMemeDB.DBFields.ItemFields.Tags]
        if mediaType:
            results['mediaType'] = item[TestMemeDB.DBFields.ItemFields.MediaType]
        if fileExt:
            results['fileExt'] = fileExt
        if mediaID:
            results['mediaID'] = mediaID
        if mediaURL:
            results['mediaURL'] = mediaURL
        if thumbnail:
            results['thumbnail'] = item[TestMemeDB.DBFields.ItemFields.Thumbnail]

        if len(results) == 1:
            return list(results.values())[0]

        return results

    def set(self, itemId, name=None, mediaType=None, fileExt=None, tags=None, mediaID=None, mediaURL=None, thumbnail=None):
        item = self.getItem(itemId)
        if item is None:
            raise Exception(f'Item ID: {itemId} does not exist')

        if name is not None:
            item[TestMemeDB.DBFields.ItemFields.Name] = name
        if tags is not None:
            item[TestMemeDB.DBFields.ItemFields.Tags] = tags
        if fileExt is not None:
            item[TestMemeDB.DBFields.ItemFields.FileExt] = fileExt
        if mediaID is not None:
            item[TestMemeDB.DBFields.ItemFields.MediaID] = mediaID
        if mediaURL is not None:
            item[TestMemeDB.DBFields.ItemFields.MediaURL] = mediaURL
        if mediaType is not None:
            item[TestMemeDB.DBFields.ItemFields.MediaType] = mediaType
        if thumbnail is not None:
            item[TestMemeDB.DBFields.ItemFields.Thumbnail] = thumbnail

    def createItem(self):
        itemId = str(self.db[TestMemeDB.DBFields.ItemCount])
        self.db[TestMemeDB.DBFields.Items][itemId] = {
            TestMemeDB.DBFields.ItemFields.ID: int(itemId),
            TestMemeDB.DBFields.ItemFields.Name: '',
            TestMemeDB.DBFields.ItemFields.MediaType: 'unknown',
            TestMemeDB.DBFields.ItemFields.FileExt: '',
            TestMemeDB.DBFields.ItemFields.Tags: [],
            TestMemeDB.DBFields.ItemFields.MediaID: '',
            TestMemeDB.DBFields.ItemFields.MediaURL: '',
            TestMemeDB.DBFields.ItemFields.Thumbnail: '',
        }
        self.db[TestMemeDB.DBFields.ItemCount] += 1
        return itemId

    def getNextID(self):
        return self.db[TestMemeDB.DBFields.ItemCount]

    def deleteItem(self, itemId):
        if not self.inDB(itemId):
            return

        # remove it from the dictionary
        self.db[TestMemeDB.DBFields.Items].pop(str(itemId))

        # decrement count
        self.db[TestMemeDB.DBFields.ItemCount] -= 1