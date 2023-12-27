from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from apiutils.FileStorageClasses.RepoLocalFileStorage import RepoLocalFileStorage
from apiutils.configs.ServerConfig import ServerConfig


def uploadLocalJSONDBToPBFS():
    """
    Saves data/db.json into PBFS so it matches
    """
    pbfs = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)
    lcfs = RepoLocalFileStorage()
    db = lcfs.getJSONDB()
    print('Writing data/db.json')
    pbfs.writeJSONDB(db)
    print('Done')

def downloadPBFSJSONDBToLocal():
    """
    Downloads the JSON db file from PBFS and saves it into local db
    """
    pbfs = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)
    lcfs = RepoLocalFileStorage()
    db = pbfs.getJSONDB()
    lcfs.writeJSONDB(db)
