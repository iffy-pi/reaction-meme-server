class MemeLibraryItem:
    def __init__(self, id:int=None, name:str=None, fileExt=None, tags:list[str]=None, cloudID=None, cloudURL=None ):
        self.id = id
        self.name =     name
        self.tags =     tags
        self.fileExt =  fileExt
        self.cloudID =  cloudID
        self.cloudURL = cloudURL


    @staticmethod
    def getDefaultName():
        return ''

    @staticmethod
    def getDefaultFileExt():
        return ''

    @staticmethod
    def getDefaultTags():
        return []

    @staticmethod
    def getDefaultCloudID():
        return ''

    @staticmethod
    def getDefaultCloudURL():
        return ''

    def setProperty(self, id:int=None, name:str=None, fileExt:str=None, tags:list[str]=None, cloudID:str=None, cloudURL:str=None):
        """
        Set the property of the meme library item, any arguments left to None will not have the property value changed
        """
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if fileExt is not None:
            self.fileExt = fileExt
        if tags is not None:
            self.tags = tags
        if cloudID is not None:
            self.cloudID = cloudID
        if cloudURL is not None:
            self.cloudURL = cloudURL

    def getID(self) -> int:
        return self.id

    def getName(self) -> str:
        return self.name

    def getTags(self) -> list[str]:
        return self.tags

    def getFileExt(self) -> str:
        return self.fileExt

    def getCloudID(self) -> str:
        return self.cloudID

    def getURL(self) -> str:
        return self.cloudURL

    def __str__(self):
        return f'Meme(id={self.id}, name="{self.name}", ext="{self.fileExt}", tags={self.tags}, cloudId={self.cloudID}, url={self.cloudURL})'