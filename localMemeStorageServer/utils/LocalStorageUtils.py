import json
import os
import socket

import requests

from apiutils.MemeUploaderClasses.LocalStorageUploader import LocalStorageUploader
from os.path import join
from apiutils.configs.ServerConfig import ServerConfig, MemeStorageOption

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

SYSTEM_IP = get_ip()

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

def makeRemotelyAccessible(localURL):
    return localURL.replace('127.0.0.1', SYSTEM_IP)

def getLocalVersionForCloudMeme(cloudID:str, cloudURL:str, fileExt:str) -> tuple[str, str]:
    """
    Returns the local ID and local URL for a meme stored in the cloud service
    If the meme does not exist in the local repository, it is downloaded from the cloudinary services
    :return tuple (local ID, local url)
    """
    cloudMapPath = os.path.join(ServerConfig.PROJECT_ROOT, 'localMemeStorageServer', 'storage', 'cloudMap.json')
    with open(cloudMapPath, 'r') as file:
        cloudMap = json.load(file)

    if cloudID in cloudMap:
        return cloudMap[cloudID]['localID'], makeRemotelyAccessible(cloudMap[cloudID]['localURL'])

    print(f'Downloading {cloudID} to local repository ({cloudURL}')

    # download the meme from cloudinary
    resp = requests.get('http://res.cloudinary.com/du6q7wdat/image/upload/v1/memes/kyxdqozu9587bgy7h75e')
    if not resp.ok:
        raise Exception('Failed URL request!')

    uploader = makeLocalStorageUploader()
    localID, localURL = uploader.uploadMedia(resp.content, fileExt)

    # update the cloud map with the new info
    cloudMap[cloudID] = {
        'cloudID': cloudID,
        'cloudURL': cloudURL,
        'localID': localID,
        'localURL': localURL
    }
    with open(cloudMapPath, 'w') as file:
        json.dump(cloudMap, file, indent=4)

    # return the info
    return localID, makeRemotelyAccessible(localURL)

def cloudMemeNeedsToBeConvertedToLocal(cloudURL) -> bool:
    """
    Returns if the given item needs to be converted into its local version
    :param cloudID:
    :param cloudURL:
    :return:
    """
    # Only allowed if in development
    if not ServerConfig.isDevEnv():
        return False

    if ServerConfig.MEME_STORAGE != MemeStorageOption.LOCAL:
        return False

    if cloudURL is None:
        return False

    # actual checking of the url
    return '127.0.0.1' not in cloudURL
