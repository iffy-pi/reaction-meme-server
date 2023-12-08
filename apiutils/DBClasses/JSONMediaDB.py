import json
import os

from apiutils.DBClasses.MediaDB import MediaDB
from apiutils.FileStorageClasses.JSONDBFileStorage import JSONDBFileStorage
from apiutils.MemeManagement.MemeLibraryItem import MemeLibraryItem

class JSONMediaDB(MediaDB):
    instance = None
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

    def __init__(self, fileStorage:JSONDBFileStorage):
        self.db = None
        self.__dbLock = False
        self.fileStorage = fileStorage

    @staticmethod
    def getSingleton():
        if JSONMediaDB.instance is None:
            raise Exception('Instance not initialized')
        return JSONMediaDB.instance

    @staticmethod
    def initSingleton(fileStorage:JSONDBFileStorage):
        JSONMediaDB.instance = JSONMediaDB(fileStorage)
    def initDB(self) -> None:
        self.__getDBLock()
        self.db = {
            JSONMediaDB.DBFields.ItemCount: 0,
            JSONMediaDB.DBFields.Items: {}
        }
        self.__releaseDBLock()

    def loadDB(self) -> None:
        self.__getDBLock()
        self.db = self.fileStorage.getJSONDB()
        self.__releaseDBLock()

    def writeDB(self) -> None:
        self.__getDBLock()
        self.fileStorage.writeJSONDB(self.db)
        self.__releaseDBLock()

    def hasItem(self, itemID:int) -> bool:
        return str(itemID) in self.db[JSONMediaDB.DBFields.Items]

    def __getJSONItem(self, itemId, lockDB=True):
        if lockDB:
            self.__getDBLock()
        it = self.db.get(JSONMediaDB.DBFields.Items).get(str(itemId))

        if lockDB:
            self.__releaseDBLock()
        return it

    def __createMemeFromJSONItem(self, jsonItem):
        return MemeLibraryItem(
            id=jsonItem[JSONMediaDB.DBFields.ItemFields.ID],
            name=jsonItem[JSONMediaDB.DBFields.ItemFields.Name],
            tags=jsonItem[JSONMediaDB.DBFields.ItemFields.Tags],
            fileExt=jsonItem[JSONMediaDB.DBFields.ItemFields.FileExt],
            cloudID=jsonItem[JSONMediaDB.DBFields.ItemFields.CloudID],
            cloudURL=jsonItem[JSONMediaDB.DBFields.ItemFields.CloudURL]
            )

    def getMemeItem(self, itemID:int) -> MemeLibraryItem:
        return self.__createMemeFromJSONItem(self.__getJSONItem(itemID))

    def __addItemToDB(self, name, fileExt, tags, cloudID, cloudURL):
        self.__getDBLock()
        itemId = str(self.db[JSONMediaDB.DBFields.ItemCount])
        self.db[JSONMediaDB.DBFields.Items][itemId] = {
            JSONMediaDB.DBFields.ItemFields.ID           : itemId,
            JSONMediaDB.DBFields.ItemFields.Name         : name,
            JSONMediaDB.DBFields.ItemFields.FileExt      : fileExt,
            JSONMediaDB.DBFields.ItemFields.Tags         : tags,
            JSONMediaDB.DBFields.ItemFields.CloudID      : cloudID,
            JSONMediaDB.DBFields.ItemFields.CloudURL     : cloudURL
        }
        self.db[JSONMediaDB.DBFields.ItemCount] += 1
        self.__releaseDBLock()
        return itemId

    def createItem(self) -> int:
        itId = self.__addItemToDB(
            MemeLibraryItem.getDefaultName(), MemeLibraryItem.getDefaultFileExt(),
            MemeLibraryItem.getDefaultTags(), MemeLibraryItem.getDefaultCloudID(),
            MemeLibraryItem.getDefaultCloudURL())
        return int(itId)

    def addMemeToDB(self, memeItem:MemeLibraryItem) -> None:
        """
        Adds a new Meme Library item to the media database
        Also updates item.id to match the ID of the item added to the database
        If a property of memeItem is None, the field in the database is initialized to its default value
        """
        itemId = self.createItem()
        memeItem.setProperty(id=itemId)
        self.updateItem(itemId, memeItem)

    def __updateItemProperty(self, itemId:int, name:str=None, tags:list[str]=None, fileExt=None, cloudID=None, cloudURL=None ):
        self.__getDBLock()
        item = self.__getJSONItem(itemId, lockDB=False)
        if name is not None:
            item[JSONMediaDB.DBFields.ItemFields.Name] = name
        if tags is not None:
            item[JSONMediaDB.DBFields.ItemFields.Tags] = tags
        if fileExt is not None:
            item[JSONMediaDB.DBFields.ItemFields.FileExt] = fileExt
        if cloudID is not None:
            item[JSONMediaDB.DBFields.ItemFields.CloudID] = cloudID
        if cloudURL is not None:
            item[JSONMediaDB.DBFields.ItemFields.CloudURL] = cloudURL
        self.__releaseDBLock()

    def updateItem(self, itemId:int, item:MemeLibraryItem):
        """
        Updates the item pointed to by itemID with the contents of memeItem
        If a property of memeItem is None, the field in the database is not updated
        """
        self.__updateItemProperty(itemId,
                                  name=item.getName(), tags=item.getTags(),
                                  fileExt=item.getFileExt(), cloudID=item.getCloudID(),
                                  cloudURL=item.getURL())

    def getAllDBMemes(self) -> list[MemeLibraryItem]:
        self.__getDBLock()
        res = [
            self.__createMemeFromJSONItem(it)
            for it in self.db.get(JSONMediaDB.DBFields.Items).values()
        ]
        self.__releaseDBLock()
        return res

    def __isDBLocked(self):
        return self.__dbLock

    def __getDBLock(self):
        while self.__isDBLocked():
            pass
        self.__dbLock = True

    def __releaseDBLock(self):
        self.__dbLock = False