class JSONDBFileStorageInterface:
    def __init__(self):
        '''
        Ancestor class which implements all the required methods used by MediaDB
        '''
        pass

    def getJSONDB(self) -> dict:
        raise Exception('Must be implemented in subclass')
    
    def writeJSONDB(self, db:dict):
        raise Exception('Must be implemented in subclass')