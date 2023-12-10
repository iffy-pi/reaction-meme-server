import json
import os
class ServerConfig:
    # When a new config is added, also update get from JSON as well
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', '..'))
    PROJECT_ENVIRONMENT = None
    CLOUDINARY_CLOUD_NAME = None
    CLOUDINARY_API_KEY = None
    CLOUDINARY_API_SECRET = None
    PBFS_ACCESS_TOKEN = None
    PBFS_SERVER_IDENTIFIER = None
    ALLOWED_ACCESS_TOKENS = None

    @staticmethod
    def setConfigFromEnv():
        #ServerConfig.PROJECT_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', '..'))
        ServerConfig.PROJECT_ENVIRONMENT = os.environ.get('RMSVR_PROJECT_ENV')
        ServerConfig.CLOUDINARY_CLOUD_NAME = os.environ.get('RMSVR_CLOUDINARY_CLOUD_NAME')
        ServerConfig.CLOUDINARY_API_KEY = os.environ.get('RMSVR_CLOUDINARY_API_KEY')
        ServerConfig.CLOUDINARY_API_SECRET = os.environ.get('RMSVR_CLOUDINARY_API_SECRET')

        ServerConfig.PBFS_ACCESS_TOKEN = os.environ.get('RMSVR_PBFS_ACCESS_TOKEN')
        ServerConfig.PBFS_SERVER_IDENTIFIER = os.environ.get('RMSVR_PBFS_SERVER_IDEN')
        ServerConfig.ALLOWED_ACCESS_TOKENS = os.environ.get('RMSVR_ACCESS_TOKENS')
        if ServerConfig.ALLOWED_ACCESS_TOKENS is not None:
            ServerConfig.ALLOWED_ACCESS_TOKENS = ServerConfig.ALLOWED_ACCESS_TOKENS.split(';')
        else:
            ServerConfig.ALLOWED_ACCESS_TOKENS = []

    @staticmethod
    def setConfigFromJSON(jsonFile):
        with open(jsonFile, "r") as file:
            loadedEnv = json.load(file)

        #ServerConfig.PROJECT_ROOT = loadedEnv['PROJECT_ROOT']
        ServerConfig.PROJECT_ENVIRONMENT = loadedEnv['PROJECT_ENVIRONMENT']
        ServerConfig.CLOUDINARY_CLOUD_NAME = loadedEnv['CLOUDINARY_CLOUD_NAME']
        ServerConfig.CLOUDINARY_API_KEY = loadedEnv['CLOUDINARY_API_KEY']
        ServerConfig.CLOUDINARY_API_SECRET = loadedEnv['CLOUDINARY_API_SECRET']
        ServerConfig.PBFS_ACCESS_TOKEN = loadedEnv['PBFS_ACCESS_TOKEN']
        ServerConfig.PBFS_SERVER_IDENTIFIER = loadedEnv['PBFS_SERVER_IDENTIFIER']
        ServerConfig.ALLOWED_ACCESS_TOKENS = loadedEnv['ALLOWED_ACCESS_TOKENS']

    @staticmethod
    def printEnv():
        print(f'PROJECT_ROOT = {ServerConfig.PROJECT_ROOT}')
        print(f'PROJECT_ENVIRONMENT = {ServerConfig.PROJECT_ENVIRONMENT}')
        print(f'CLOUDINARY_CLOUD_NAME = {ServerConfig.CLOUDINARY_CLOUD_NAME}')
        print(f'CLOUDINARY_API_KEY = {ServerConfig.CLOUDINARY_API_KEY}')
        print(f'CLOUDINARY_API_SECRET = {ServerConfig.CLOUDINARY_API_SECRET}')
        print(f'PBFS_ACCESS_TOKEN = {ServerConfig.PBFS_ACCESS_TOKEN}')
        print(f'PBFS_SERVER_IDENTIFIER = {ServerConfig.PBFS_SERVER_IDENTIFIER}')
        print(f'ALLOWED_ACCESS_TOKENS = {ServerConfig.ALLOWED_ACCESS_TOKENS}')

    @staticmethod
    def isDevEnv():
        return ServerConfig.PROJECT_ENVIRONMENT is None or ServerConfig.PROJECT_ENVIRONMENT.lower() != 'production'
