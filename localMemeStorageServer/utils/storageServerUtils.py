from apiutils.MemeUploaderClasses.LocalStorageUploader import LocalStorageUploader
from os.path import join
from apiutils.configs.ServerConfig import ServerConfig

def getMemeDir():
    return join(ServerConfig.PROJECT_ROOT, "localMemeStorageServer", "storage", "memes")


def getConfigJSONPath():
    return join(ServerConfig.PROJECT_ROOT, "localMemeStorageServer", "storage", "config.json")

def makeLocalStorageUploader():
    return LocalStorageUploader(
        getConfigJSONPath(),
        getMemeDir(),
        addUploadedFlag=True
    )