from apiutils.MemeManagement.MemeDBInterface import MemeDBInterface, MemeDBException
from apiutils.FileStorageClasses.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.MemeManagement.MemeContainer import MemeContainer
from apiutils.MemeManagement.MemeMediaType import MemeMediaType, getMediaTypeFromValue


class JSONMemeDB(MemeDBInterface):
    instance = None
    class DBFields:
        ItemCount = "itemCount"
        Items = "items"
        class ItemFields:
            ID = 'id'
            Name = "name"
            Type = "type"
            FileExt = "fileExt"
            Tags = "tags"
            CloudID = "cloudID"
            CloudURL = "cloudURL"

    def __init__(self, fileStorage:JSONDBFileStorageInterface):
        self.db = None
        self.__dbLock = False
        self.fileStorage = fileStorage

    @staticmethod
    def getSingleton():
        if JSONMemeDB.instance is None:
            raise Exception('Instance not initialized')
        return JSONMemeDB.instance

    @staticmethod
    def initSingleton(fileStorage:JSONDBFileStorageInterface):
        JSONMemeDB.instance = JSONMemeDB(fileStorage)

    def initDB(self) -> None:
        self.__getDBLock()
        self.db = {
            JSONMemeDB.DBFields.ItemCount: 0,
            JSONMemeDB.DBFields.Items: {}
        }
        self.__releaseDBLock()

    def isDBLoaded(self) -> bool:
        return self.db is not None

    def loadDB(self) -> bool:
        self.__getDBLock()
        self.db = self.fileStorage.getJSONDB()
        res = self.db is not None
        self.__releaseDBLock()
        return res

    def unloadDB(self) -> bool:
        if not self.isDBLoaded():
            return True

        # removes all the keys in the dict
        self.db.clear()
        self.db = None
        return True

    def __errIfUnloadedDB(self):
        if not self.isDBLoaded():
            raise MemeDBException("Database has not been loaded!")

    def writeDB(self) -> bool:
        self.__errIfUnloadedDB()
        self.__getDBLock()
        res =  self.fileStorage.writeJSONDB(self.db)
        self.__releaseDBLock()
        return res

    def hasItem(self, itemID:int) -> bool:
        self.__errIfUnloadedDB()
        return str(itemID) in self.db[JSONMemeDB.DBFields.Items]

    def __getJSONItem(self, itemId, lockDB=True):
        self.__errIfUnloadedDB()
        if lockDB:
            self.__getDBLock()
        it = self.db.get(JSONMemeDB.DBFields.Items).get(str(itemId))

        if lockDB:
            self.__releaseDBLock()
        return it

    def __createMemeFromJSONItem(self, jsonItem):
        return MemeContainer(
            id=jsonItem[JSONMemeDB.DBFields.ItemFields.ID],
            name=jsonItem[JSONMemeDB.DBFields.ItemFields.Name],
            type=getMediaTypeFromValue(jsonItem[JSONMemeDB.DBFields.ItemFields.Type]),
            tags=jsonItem[JSONMemeDB.DBFields.ItemFields.Tags],
            fileExt=jsonItem[JSONMemeDB.DBFields.ItemFields.FileExt],
            cloudID=jsonItem[JSONMemeDB.DBFields.ItemFields.CloudID],
            cloudURL=jsonItem[JSONMemeDB.DBFields.ItemFields.CloudURL]
            )

    def getMemeItem(self, itemID:int) -> MemeContainer:
        return self.__createMemeFromJSONItem(self.__getJSONItem(itemID))

    def __addItemToDB(self, name:str, type:MemeMediaType, fileExt:str, tags:list[str], cloudID:str, cloudURL:str):
        self.__errIfUnloadedDB()
        self.__getDBLock()
        itemId = str(self.db[JSONMemeDB.DBFields.ItemCount])
        self.db[JSONMemeDB.DBFields.Items][itemId] = {
            JSONMemeDB.DBFields.ItemFields.ID           : int(itemId),
            JSONMemeDB.DBFields.ItemFields.Name         : name,
            JSONMemeDB.DBFields.ItemFields.Type         : type.value,
            JSONMemeDB.DBFields.ItemFields.FileExt      : fileExt,
            JSONMemeDB.DBFields.ItemFields.Tags         : tags,
            JSONMemeDB.DBFields.ItemFields.CloudID      : cloudID,
            JSONMemeDB.DBFields.ItemFields.CloudURL     : cloudURL
        }
        self.db[JSONMemeDB.DBFields.ItemCount] += 1
        self.__releaseDBLock()
        return itemId

    def createItem(self) -> int:
        itId = self.__addItemToDB(
            MemeContainer.getDefaultName(),
            MemeMediaType.UNKNOWN,
            MemeContainer.getDefaultFileExt(),
            MemeContainer.getDefaultTags(),
            MemeContainer.getDefaultCloudID(),
            MemeContainer.getDefaultCloudURL())
        return int(itId)

    def addMemeToDB(self, memeItem:MemeContainer) -> bool:
        """
        Adds a new Meme Library item to the media database
        Also updates item.id to match the ID of the item added to the database
        If a property of memeItem is None, the field in the database is initialized to its default value
        """
        itemId = self.createItem()
        memeItem.setProperty(id=itemId)
        return self.updateItem(itemId, memeItem)

    def __updateItemProperty(self, itemId:int, name:str=None, type:MemeMediaType=None, tags:list[str]=None, fileExt=None, cloudID=None, cloudURL=None ) -> bool:
        self.__errIfUnloadedDB()
        self.__getDBLock()
        item = self.__getJSONItem(itemId, lockDB=False)

        if item is None:
            self.__releaseDBLock()
            return False

        if name is not None:
            item[JSONMemeDB.DBFields.ItemFields.Name] = name
        if tags is not None:
            item[JSONMemeDB.DBFields.ItemFields.Tags] = tags
        if fileExt is not None:
            item[JSONMemeDB.DBFields.ItemFields.FileExt] = fileExt
        if cloudID is not None:
            item[JSONMemeDB.DBFields.ItemFields.CloudID] = cloudID
        if cloudURL is not None:
            item[JSONMemeDB.DBFields.ItemFields.CloudURL] = cloudURL
        if type is not None:
            item[JSONMemeDB.DBFields.ItemFields.Type] = type.value

        self.__releaseDBLock()

        return True

    def updateItem(self, itemId:int, item:MemeContainer) -> bool:
        """
        Updates the item pointed to by itemID with the contents of memeItem
        If a property of memeItem is None, the field in the database is not updated
        """
        return self.__updateItemProperty(itemId,
                                  name=item.getName(), type=item.getType(), tags=item.getTags(),
                                  fileExt=item.getFileExt(), cloudID=item.getCloudID(),
                                  cloudURL=item.getURL())

    def getGroupOfMemes(self, itemsPerPage:int, pageNo:int) -> list[MemeContainer]:
        self.__errIfUnloadedDB()
        itemIds = list(self.db.get(JSONMemeDB.DBFields.Items).keys())
        itemCount = len(itemIds)
        startOffset = (pageNo-1)  * itemsPerPage

        if startOffset >= itemCount:
            return []


        selectedIds = itemIds[startOffset: min(itemCount, startOffset+itemsPerPage)]
        return [ self.getMemeItem(i) for i in selectedIds]

    def getAllDBMemes(self) -> list[MemeContainer]:
        self.__errIfUnloadedDB()
        self.__getDBLock()
        res = [
            self.__createMemeFromJSONItem(it)
            for it in self.db.get(JSONMemeDB.DBFields.Items).values()
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