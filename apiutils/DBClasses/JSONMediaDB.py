import json
import os

from apiutils.DBClasses.MediaDB import MediaDB
from apiutils.MemeManagement.MemeLibraryItem import MemeLibraryItem
from apiutils.configs.config import PROJECT_ROOT


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

    def __init__(self):
        self.dbFilePath = os.path.join(PROJECT_ROOT, 'data', 'db.json')
        self.db = None

    @staticmethod
    def getInstance():
        if JSONMediaDB.instance is None:
            JSONMediaDB.instance = JSONMediaDB()
        return JSONMediaDB.instance

    def initDB(self) -> None:
        self.db = {
            JSONMediaDB.DBFields.ItemCount: 0,
            JSONMediaDB.DBFields.Items: {}
        }

    def loadDB(self) -> None:
        with open(self.dbFilePath, 'r') as file:
            self.db = json.load(file)

    def writeDB(self) -> None:
        with open(self.dbFilePath, 'w') as file:
            json.dump(self.db, file, indent=4)

    def hasItem(self, itemID:int) -> bool:
        return str(itemID) in self.db[JSONMediaDB.DBFields.Items]

    def __getJSONItem(self, itemId):
        return self.db.get(JSONMediaDB.DBFields.Items).get(str(itemId))

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
        item = self.__getJSONItem(itemId)
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
        return [
            self.__createMemeFromJSONItem(it)
            for it in self.db.get(JSONMediaDB.DBFields.Items).values()
        ]