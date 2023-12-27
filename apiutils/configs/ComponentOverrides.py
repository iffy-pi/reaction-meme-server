import os

from apiutils.FileStorageClasses.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from apiutils.FileStorageClasses.RepoLocalFileStorage import RepoLocalFileStorage
from apiutils.MemeManagement.MemeLibrary import MemeLibrary
from apiutils.MemeManagement.MemeUploaderInterface import MemeUploaderInterface
from apiutils.MemeUploaderClasses.CloudinaryUploader import CloudinaryUploader
from apiutils.configs.ServerConfig import ServerConfig, JSONDBFileStorageOption, MemeStorageOption
from localMemeStorageServer.utils.LocalStorageUtils import makeLocalStorageUploader


def getServerFileStorage() -> JSONDBFileStorageInterface:
    if ServerConfig.JSON_DB_FILE_STORAGE == JSONDBFileStorageOption.LOCAL:
        return RepoLocalFileStorage()
    elif ServerConfig.JSON_DB_FILE_STORAGE == JSONDBFileStorageOption.PBFS:
        return PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)
    else:
        raise Exception(f'Unrecognized file storage: "{ServerConfig.JSON_DB_FILE_STORAGE}"')


def getServerMemeUploader() -> MemeUploaderInterface:
    if ServerConfig.MEME_STORAGE == MemeStorageOption.LOCAL:
        return makeLocalStorageUploader()
    elif ServerConfig.MEME_STORAGE == MemeStorageOption.CLOUDINARY:
        return CloudinaryUploader()
    else:
        raise Exception(f'Unrecognized meme storage: "{ServerConfig.MEME_STORAGE}"')


def loadLibrary(memeLib:MemeLibrary, verbose:bool=True):
    INIT_LIB_FROM_CATALOG_OVERRIDE = os.environ.get('INIT_LIB_FROM_CATALOG_OVERRIDE') is not None
    if INIT_LIB_FROM_CATALOG_OVERRIDE:
        if verbose: print('OVERRIDE - Library Source: catalog.csv')
        memeLib.makeLibraryFromCSV(os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'catalog.csv'))
    else:
        if verbose: print('Library Source: database')
        memeLib.loadLibrary()