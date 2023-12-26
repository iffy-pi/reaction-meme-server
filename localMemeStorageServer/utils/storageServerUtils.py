import os

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


def getMemeFileName(id):
    for filename in os.listdir(getMemeDir()):
        if filename.startswith(f"meme_{id}"):
            return filename

    return None
