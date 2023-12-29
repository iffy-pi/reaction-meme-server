from apiutils.MemeManagement.MemeContainer import MemeContainer

class MemeDBException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MemeDBInterface:
    """
    Interface that must be implemented by classes which host the database for the MemeLibrary
    """
    def __init__(self):
        pass

    def initDB(self) -> None:
        """
        Initializes the database with data
        """
        raise Exception("Must implement in subclass")

    def loadDB(self) -> bool:
        """
        Load the database with data from actual database
        Returns true if the operation was completed successfully.
        """
        raise Exception("Must implement in subclass")

    def isDBLoaded(self) -> bool:
        """
        Returns a boolean value if the database has been loaded/connected to
        """
        raise Exception("Must implement in subclass")

    def unloadDB(self) -> bool:
        """
        Unloads the database (all its objects and memory) from system
        Returns true if the operation was completed successfully.
        """
        raise Exception("Must implement in subclass")

    def writeDB(self) -> bool:
        """
        Writes the database object to the actual database file
        Returns true if the operation was completed successfully.
        """
        raise Exception("Must implement in subclass")

    def hasItem(self, itemID:int) -> bool:
        """
        Returns if the database contains the item id
        :param itemID: The ID of the item
        :return: boolean -> True if the ID is in the database, false if it isnt
        """
        raise Exception("Must implement in subclass")

    def getMemeItem(self, itemID:int) -> MemeContainer:
        """
        Returns a Meme Library Item for the given itemID
        """
        raise Exception("Must implement in subclass")

    def createItem(self) -> int:
        """
        Creates an item in the database and returns the itemID
        Returns -1 if item was failed to be created
        """
        raise Exception("Must implement in subclass")

    def addMemeToDB(self, item:MemeContainer) -> bool:
        """
        Adds a new Meme Library item to the media database
        Also updates item.id to match the ID of the item added to the database
        If a property of memeItem is None, the field in the database is initialized to its default value
        Returns true if the operation was completed successfully.
        """
        raise Exception("Must implement in subclass")

    def updateItem(self, itemId:int, memeItem:MemeContainer) -> bool:
        """
        Updates the item pointed to by itemID with the contents of memeItem
        If a property of memeItem is None, the field in the database should not updated
        Returns true if the operation was completed successfully.
        """
        raise Exception('Must implement in subclass')


    def getGroupOfMemes(self, itemsPerPage:int, pageNo:int) -> list[MemeContainer]:
        """
        Gets a set of memes from a given page
        :param itemsPerPage: The number of memes per page
        :param pageNo: The page number
        :return: The list of Memes retrieved
        """
        raise Exception('Must implement in subclass')

    def getAllDBMemes(self) -> list[MemeContainer]:
        """
        Returns a list of all the memes in the database
        :return:
        """
        raise Exception("Must implement in subclass")

