import json
import os
from enum import Enum

class MemeDBOption(Enum):
    JSON = 'json'
    NONE = 'none'

class MemeStorageOption(Enum):
    NONE = 'none'
    LOCAL = 'local'
    CLOUDINARY = 'cloudinary'

class JSONDBFileStorageOption(Enum):
    NONE = 'none'
    LOCAL = 'local'
    PBFS = 'pbfs'

class ProjectEnvironment(Enum):
    PROD = 'production'
    DEV = 'development'
    TESTING = 'testing'


def getTypeForValString(enumType, valStr: str):
    valStr = valStr.lower()
    listOfTypes = list(enumType.__members__.values())
    for t in listOfTypes:
        if valStr == t.value:
            return t
    raise Exception(f'Unknown type "{valStr}" for type list: {listOfTypes}')

class ServerConfig:
    # When a new config is added, also update get from JSON as well
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', '..'))
    # Default values for the configuration
    PROJECT_ENVIRONMENT = ProjectEnvironment.DEV
    CLOUDINARY_CLOUD_NAME = ''
    CLOUDINARY_API_KEY = ''
    CLOUDINARY_API_SECRET = ''
    MEME_DB = MemeDBOption.JSON
    MEME_STORAGE = MemeStorageOption.CLOUDINARY
    JSON_DB_FILE_STORAGE = JSONDBFileStorageOption.PBFS
    PBFS_ACCESS_TOKEN = ''
    PBFS_SERVER_IDENTIFIER = ''
    ALLOWED_ACCESS_TOKENS = []

    @staticmethod
    def getConfigDict():
        return {
            'PROJECT_ROOT': ServerConfig.PROJECT_ROOT,
            'PROJECT_ENVIRONMENT': ServerConfig.PROJECT_ENVIRONMENT,
            'CLOUDINARY_CLOUD_NAME': ServerConfig.CLOUDINARY_CLOUD_NAME,
            'CLOUDINARY_API_KEY': ServerConfig.CLOUDINARY_API_KEY,
            'CLOUDINARY_API_SECRET': ServerConfig.CLOUDINARY_API_SECRET,
            'MEME_DB': ServerConfig.MEME_DB,
            'MEME_STORAGE': ServerConfig.MEME_STORAGE,
            'JSON_DB_FILE_STORAGE': ServerConfig.JSON_DB_FILE_STORAGE,
            'PBFS_ACCESS_TOKEN': ServerConfig.PBFS_ACCESS_TOKEN,
            'PBFS_SERVER_IDENTIFIER': ServerConfig.PBFS_SERVER_IDENTIFIER,
            'ALLOWED_ACCESS_TOKENS': ServerConfig.ALLOWED_ACCESS_TOKENS
        }

    @staticmethod
    def getSensitiveDataDict():
        # If a config is sensitive (should not be accessed by anyone)
        return {
            'PROJECT_ROOT': True,
            'PROJECT_ENVIRONMENT': False,
            'CLOUDINARY_CLOUD_NAME': True,
            'CLOUDINARY_API_KEY': True,
            'CLOUDINARY_API_SECRET': True,
            'MEME_DB': False,
            'MEME_STORAGE': False,
            'JSON_DB_FILE_STORAGE': False,
            'PBFS_ACCESS_TOKEN': True,
            'PBFS_SERVER_IDENTIFIER': True,
            'ALLOWED_ACCESS_TOKENS': True
        }

    @staticmethod
    def setConfigFromEnvDict(env: dict):
        projEnv = env.get('RMSVR_PROJECT_ENVIRONMENT')
        cloudName = env.get('RMSVR_CLOUDINARY_CLOUD_NAME')
        apiKey = env.get('RMSVR_CLOUDINARY_API_KEY')
        apiSecret = env.get('RMSVR_CLOUDINARY_API_SECRET')
        memeDB = env.get('RMSVR_MEME_DB')
        memeStorage = env.get('RMSVR_MEME_STORAGE')
        dbFileStorage = env.get('RMSVR_JSON_DB_FILE_STORAGE')
        pbfsAccessToken = env.get('RMSVR_PBFS_ACCESS_TOKEN')
        pbfsServerIden = env.get('RMSVR_PBFS_SERVER_IDENTIFIER')
        allowedAccessTokens = env.get('RMSVR_ALLOWED_ACCESS_TOKENS')

        if projEnv is not None:
            ServerConfig.PROJECT_ENVIRONMENT = getTypeForValString(ProjectEnvironment, projEnv)

        if cloudName is not None:
            ServerConfig.CLOUDINARY_CLOUD_NAME = cloudName

        if apiKey is not None:
            ServerConfig.CLOUDINARY_API_KEY = apiKey

        if apiSecret is not None:
            ServerConfig.CLOUDINARY_API_SECRET = apiSecret

        if memeDB is not None:
            ServerConfig.MEME_DB = getTypeForValString(MemeDBOption, memeDB)

        if memeStorage is not None:
            ServerConfig.MEME_STORAGE = getTypeForValString(MemeStorageOption, memeStorage)

        if dbFileStorage is not None:
            ServerConfig.JSON_DB_FILE_STORAGE = getTypeForValString(JSONDBFileStorageOption,
                                                                dbFileStorage)

        if pbfsAccessToken is not None:
            ServerConfig.PBFS_ACCESS_TOKEN = pbfsAccessToken

        if pbfsServerIden is not None:
            ServerConfig.PBFS_SERVER_IDENTIFIER = pbfsServerIden

        if pbfsAccessToken is not None:
            ServerConfig.PBFS_ACCESS_TOKEN = pbfsAccessToken

        if allowedAccessTokens is not None:
            ServerConfig.ALLOWED_ACCESS_TOKENS = allowedAccessTokens.split(';')

    @staticmethod
    def checkForOSOverrides():
        memeDbOverride = os.environ.get('OVERRIDE_RMSVR_MEME_DB')
        memeStorageOverride = os.environ.get('OVERRIDE_RMSVR_MEME_STORAGE')
        dbFileStorageOverride = os.environ.get('OVERRIDE_RMSVR_JSON_DB_FILE_STORAGE')

        if memeDbOverride is not None:
            ServerConfig.MEME_DB = getTypeForValString(MemeDBOption, memeDbOverride)
            print(f'OVERRIDE OF MEME_DB = {ServerConfig.MEME_DB}')

        if memeStorageOverride is not None:
            ServerConfig.MEME_STORAGE = getTypeForValString(MemeStorageOption, memeStorageOverride)
            print(f'OVERRIDE OF MEME_STORAGE = {ServerConfig.MEME_STORAGE}')

        if dbFileStorageOverride is not None:
            ServerConfig.JSON_DB_FILE_STORAGE = getTypeForValString(JSONDBFileStorageOption, dbFileStorageOverride)
            print(f'OVERRIDE OF JSON_DB_FILE_STORAGE = {ServerConfig.JSON_DB_FILE_STORAGE}')

    @staticmethod
    def setConfigFromEnv():
        ServerConfig.setConfigFromEnvDict(dict(os.environ))

    @staticmethod
    def setConfigFromJSON(jsonFile):
        with open(jsonFile, "r") as file:
            loadedEnv = json.load(file)
        ServerConfig.setConfigFromEnvDict(loadedEnv)

    @staticmethod
    def initConfig():
        # If there is a JSON env option use it
        jsonEnv = os.environ.get('JSON_CONFIG')
        if jsonEnv is not None and os.path.exists(jsonEnv):
            print(f'Initializing from JSON_CONFIG env variable: "{jsonEnv}"')
            ServerConfig.setConfigFromJSON(jsonEnv)
        else:
            ServerConfig.setConfigFromEnv()

        # check for any overrides
        ServerConfig.checkForOSOverrides()


    @staticmethod
    def saveConfigToJSON(filePath):
        props = ServerConfig.getConfigDict()
        props['PROJECT_ENVIRONMENT'] = props['PROJECT_ENVIRONMENT'].value
        props['MEME_DB'] =  props['MEME_DB'].value
        props['MEME_STORAGE'] =  props['MEME_STORAGE'].value
        props['JSON_DB_FILE_STORAGE'] =  props['JSON_DB_FILE_STORAGE'].value
        props['ALLOWED_ACCESS_TOKENS'] = ','.join(props['ALLOWED_ACCESS_TOKENS'])
        jsonDict = dict()
        for ky in props:
            jsonDict[f'RMSVR_{ky}'] = props[ky]

        with open(filePath, "w") as file:
            json.dump(jsonDict, file, indent=4)


    @staticmethod
    def printConfig(showSensitive=False):
        """
        If sensitive is true, sensitive information is not printed (replaced with *)
        """
        props = ServerConfig.getConfigDict()
        maxWidth = max([len(ky) for ky in props])
        sensData = ServerConfig.getSensitiveDataDict()

        printFormat = '{:<' + str(maxWidth) + 's} : {}'
        for ky in props:
            val = '********' if not showSensitive and sensData[ky] else props[ky]
            print(printFormat.format(ky, val))

    @staticmethod
    def isDevEnv():
        return ServerConfig.PROJECT_ENVIRONMENT == ProjectEnvironment.DEV

    @staticmethod
    def path(*paths) -> str:
        """
        Returns the full path of the item, with the project root included
        You can pass in path arguments e.g. ('folder', 'folder2', 'test.txt')
        Or a forward-slash separated argument e.g. ('folder/folder2/test.txt')
        """
        pathList = []
        for p in paths:
            pathList += p.split('/')

        paths = (ServerConfig.PROJECT_ROOT,) + tuple(pathList)
        return os.path.join(*paths)

    @classmethod
    def isTestEnv(cls):
        return ServerConfig.PROJECT_ENVIRONMENT == ProjectEnvironment.TESTING

