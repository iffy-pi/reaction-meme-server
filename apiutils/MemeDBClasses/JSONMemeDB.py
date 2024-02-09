from apiutils.MemeManagement.MemeDBInterface import MemeDBInterface, MemeDBException
from apiutils.FileStorageClasses.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.MemeManagement.MemeContainer import MemeContainer
from apiutils.MemeManagement.MemeMediaType import stringToMemeMediaType


class JSONMemeDB(MemeDBInterface):
    instance = None
    class DBFields:
        NextID = "nextID"
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

    def __isDBLocked(self):
        return self.__dbLock

    def __getDBLock(self):
        while self.__isDBLocked():
            pass
        self.__dbLock = True

    def __releaseDBLock(self):
        self.__dbLock = False

    def __errIfUnloadedDB(self):
        if not self.isDBLoaded():
            raise MemeDBException("Database has not been loaded!")

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
            mediaTypeStr=jsonItem[JSONMemeDB.DBFields.ItemFields.MediaType],
            tags=jsonItem[JSONMemeDB.DBFields.ItemFields.Tags],
            fileExt=jsonItem[JSONMemeDB.DBFields.ItemFields.FileExt],
            mediaID=jsonItem[JSONMemeDB.DBFields.ItemFields.MediaID],
            mediaURL=jsonItem[JSONMemeDB.DBFields.ItemFields.MediaURL],
            thumbnail=jsonItem[JSONMemeDB.DBFields.ItemFields.Thumbnail]
            )

    def genNewID(self, lockdb=True) -> int:
        self.__errIfUnloadedDB()

        if lockdb:
            self.__getDBLock()

        newId = self.db[JSONMemeDB.DBFields.NextID]
        while str(newId) in self.db[JSONMemeDB.DBFields.Items]:
            # If the id already exists, just skip it
            newId += 1

        # Increment it
        self.db[JSONMemeDB.DBFields.NextID] = newId + 1

        if lockdb:
            self.__releaseDBLock()

        return newId

    def __addItemToDB(self, meme:MemeContainer):
        self.__errIfUnloadedDB()
        self.__getDBLock()
        itemId = str(self.genNewID(lockdb=False))

        self.db[JSONMemeDB.DBFields.Items][itemId] = {
            JSONMemeDB.DBFields.ItemFields.ID           : int(itemId),
            JSONMemeDB.DBFields.ItemFields.Name         : meme.getName(),
            JSONMemeDB.DBFields.ItemFields.MediaType    : meme.getMediaTypeString(),
            JSONMemeDB.DBFields.ItemFields.FileExt      : meme.getFileExt(),
            JSONMemeDB.DBFields.ItemFields.Tags         : meme.getTags(),
            JSONMemeDB.DBFields.ItemFields.MediaID      : meme.getMediaID(),
            JSONMemeDB.DBFields.ItemFields.MediaURL     : meme.getMediaURL(),
            JSONMemeDB.DBFields.ItemFields.Thumbnail    : meme.getThumbnail(),
        }

        self.__releaseDBLock()
        return itemId

    def __updateItemProperty(self, itemId:int, meme:MemeContainer) -> bool:
        self.__errIfUnloadedDB()
        self.__getDBLock()
        item = self.__getJSONItem(itemId, lockDB=False)

        if item is None:
            self.__releaseDBLock()
            return False

        name = meme.getName()
        tags = meme.getTags()
        fileExt = meme.getFileExt()
        mediaID = meme.getMediaID()
        mediaURL = meme.getMediaURL()
        mediaType = meme.getMediaTypeString()
        thumbnail = meme.getThumbnail()

        if name is not None:
            item[JSONMemeDB.DBFields.ItemFields.Name] = name
        if tags is not None:
            item[JSONMemeDB.DBFields.ItemFields.Tags] = tags
        if fileExt is not None:
            item[JSONMemeDB.DBFields.ItemFields.FileExt] = fileExt
        if mediaID is not None:
            item[JSONMemeDB.DBFields.ItemFields.MediaID] = mediaID
        if mediaURL is not None:
            item[JSONMemeDB.DBFields.ItemFields.MediaURL] = mediaURL
        if mediaType is not None:
            item[JSONMemeDB.DBFields.ItemFields.MediaType] = mediaType
        if thumbnail is not None:
            item[JSONMemeDB.DBFields.ItemFields.Thumbnail] = thumbnail

        self.__releaseDBLock()

        return True

    def initDB(self) -> None:
        self.__getDBLock()
        self.db = {
            JSONMemeDB.DBFields.NextID: 0,
            JSONMemeDB.DBFields.Items: {}
        }
        self.__releaseDBLock()

    def loadDB(self) -> bool:
        self.__getDBLock()
        self.db = self.fileStorage.getJSONDB()
        res = self.db is not None
        self.__releaseDBLock()
        return res

    def isDBLoaded(self) -> bool:
        return self.db is not None

    def unloadDB(self) -> bool:
        if not self.isDBLoaded():
            return True

        # removes all the keys in the dict
        self.db.clear()
        self.db = None
        return True

    def writeDB(self) -> bool:
        self.__errIfUnloadedDB()
        self.__getDBLock()
        res =  self.fileStorage.writeJSONDB(self.db)
        self.__releaseDBLock()
        return res

    def hasMeme(self, memeID:int) -> bool:
        self.__errIfUnloadedDB()
        return str(memeID) in self.db[JSONMemeDB.DBFields.Items]

    def getMeme(self, itemID:int) -> MemeContainer:
        return self.__createMemeFromJSONItem(self.__getJSONItem(itemID))

    def createMeme(self) -> int:
        itId = self.__addItemToDB(MemeContainer.makeEmptyMeme())
        return int(itId)

    def addMemeToDB(self, memeItem:MemeContainer) -> bool:
        """
        Adds a new Meme Library item to the media database
        Also updates item.id to match the ID of the item added to the database
        If a property of memeItem is None, the field in the database is initialized to its default value
        """
        itemId = self.createMeme()
        memeItem.setProperty(id=itemId)
        return self.updateMeme(itemId, memeItem)

    def updateMeme(self, itemId:int, item:MemeContainer) -> bool:
        """
        Updates the item pointed to by itemID with the contents of memeItem
        If a property of memeItem is None, the field in the database is not updated
        """
        return self.__updateItemProperty(itemId, item)

    def getGroupOfMemes(self, itemsPerPage:int, pageNo:int) -> list[MemeContainer]:
        self.__errIfUnloadedDB()
        itemIds = list(self.db.get(JSONMemeDB.DBFields.Items).keys())
        itemCount = len(itemIds)
        startOffset = (pageNo-1)  * itemsPerPage

        if startOffset >= itemCount:
            return []


        selectedIds = itemIds[startOffset: min(itemCount, startOffset+itemsPerPage)]
        return [self.getMeme(i) for i in selectedIds]

    def getAllDBMemes(self) -> list[MemeContainer]:
        self.__errIfUnloadedDB()
        self.__getDBLock()
        res = [
            self.__createMemeFromJSONItem(it)
            for it in self.db.get(JSONMemeDB.DBFields.Items).values()
        ]
        self.__releaseDBLock()
        return res