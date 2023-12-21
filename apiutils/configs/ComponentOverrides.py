import os

from apiutils.FileStorageClasses.JSONDBFileStorageInterface import JSONDBFileStorageInterface
from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from apiutils.FileStorageClasses.RepoLocalFileStorage import RepoLocalFileStorage
from apiutils.MemeManagement.MemeLibrary import MemeLibrary
from apiutils.MemeManagement.MemeUploaderInterface import MemeUploaderInterface
from apiutils.MemeUploaderClasses.CloudinaryUploader import CloudinaryUploader
from apiutils.configs.ServerConfig import ServerConfig
from localMemeStorageServer.utils.storageServerUtils import makeLocalStorageUploader


def getServerFileStorage(verbose=True) -> JSONDBFileStorageInterface:
    FILE_STORAGE_OVERRIDE = os.environ.get('FILE_STORAGE_OVERRIDE')
    if FILE_STORAGE_OVERRIDE is not None:
        FILE_STORAGE_OVERRIDE = FILE_STORAGE_OVERRIDE.lower()

        if FILE_STORAGE_OVERRIDE == 'local':
            if verbose: print('OVERRIDE - File Storage: RepoLocal')
            fileStorage = RepoLocalFileStorage()
        elif FILE_STORAGE_OVERRIDE == 'pbfs':
            if verbose: print('OVERRIDE - File Storage: PBFS')
            fileStorage = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)
        else:
            raise Exception(f'Unrecognized file storage override key: "{FILE_STORAGE_OVERRIDE}"')

    else:
        if verbose: print('File Storage: PBFS')
        fileStorage = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)

    return fileStorage


def getServerMemeUploader(verbose=True) -> MemeUploaderInterface:
    MEME_STORAGE_OVERRIDE = os.environ.get('MEME_STORAGE_OVERRIDE')
    if MEME_STORAGE_OVERRIDE is not None:
        MEME_STORAGE_OVERRIDE = MEME_STORAGE_OVERRIDE.lower()

        if MEME_STORAGE_OVERRIDE == 'local':
            if verbose: print('OVERRIDE - Meme Storage: Local')
            memeUploader = makeLocalStorageUploader()
        elif MEME_STORAGE_OVERRIDE == 'pbfs':
            if verbose: print('OVERRIDE - Meme Storage: Cloudinary')
            memeUploader = CloudinaryUploader()
        else:
            raise Exception(f'Unrecognized meme storage override key: "{MEME_STORAGE_OVERRIDE}"')

    else:
        if verbose: print('Meme Storage: Local')
        memeUploader = makeLocalStorageUploader()

    return memeUploader


def loadLibrary(memeLib:MemeLibrary, verbose:bool=True):
    INIT_LIB_FROM_CATALOG_OVERRIDE = os.environ.get('INIT_LIB_FROM_CATALOG_OVERRIDE') is not None
    if INIT_LIB_FROM_CATALOG_OVERRIDE:
        if verbose: print('OVERRIDE - Library Source: catalog.csv')
        memeLib.makeLibraryFromCSV(os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'catalog.csv'))
    else:
        if verbose: print('Library Source: database')
        memeLib.loadLibrary()