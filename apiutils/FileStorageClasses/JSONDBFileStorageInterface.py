class JSONDBFileStorageInterface:
    def __init__(self):
        '''
        Ancestor class which implements all the required methods used by MediaDB
        '''
        pass

    def getJSONDB(self) -> dict:
        raise Exception('Must be implemented in subclass')
    
    def writeJSONDB(self, db:dict) -> bool:
        """
        Writes the JSOB db to the file storage
        Returns true if the operation was completed successfully
        """
        raise Exception('Must be implemented in subclass')