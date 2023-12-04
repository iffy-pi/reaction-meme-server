class MediaDBFileServer:
    def __init__(self):
        '''
        Ancestor class which implements all the required methods used by MediaDB
        '''
        pass

    def loadDBFromJSON(self):
        raise Exception('Must be implemented in subclass')
    
    def writeJSONDB(self, db):
        raise Exception('Must be implemented in subclass')