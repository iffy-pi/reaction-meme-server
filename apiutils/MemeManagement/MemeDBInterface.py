from apiutils.MemeManagement.MemeLibraryItem import MemeLibraryItem

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

    def loadDB(self) -> None:
        """
        Load the database with data from actual database
        """
        raise Exception("Must implement in subclass")

    def writeDB(self) -> None:
        """
        Writes the database object to the actual database file
        """
        raise Exception("Must implement in subclass")

    def hasItem(self, itemID:int) -> bool:
        """
        Returns if the database contains the item id
        :param itemID: The ID of the item
        :return: boolean -> True if the ID is in the database, false if it isnt
        """
        raise Exception("Must implement in subclass")

    def getMemeItem(self, itemID:int) -> MemeLibraryItem:
        """
        Returns a Meme Library Item for the given itemID
        """
        raise Exception("Must implement in subclass")

    def createItem(self) -> int:
        """
        Creates an item in the database and returns the itemID
        """
        raise Exception("Must implement in subclass")

    def addMemeToDB(self, item:MemeLibraryItem) -> None:
        """
        Adds a new Meme Library item to the media database
        Also updates item.id to match the ID of the item added to the database
        If a property of memeItem is None, the field in the database is initialized to its default value
        """
        raise Exception("Must implement in subclass")

    def updateItem(self, itemId:int, memeItem:MemeLibraryItem):
        """
        Updates the item pointed to by itemID with the contents of memeItem
        If a property of memeItem is None, the field in the database is not updated
        """
        raise Exception('Must implement in subclass')

    def getAllDBMemes(self) -> list[MemeLibraryItem]:
        """
        Returns a list of all the memes in the database
        :return:
        """
        raise Exception("Must implement in subclass")

