import json
import os
import socket

import requests

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
    return ServerConfig.path('localMemeStorageServer/storage/memes')


def getConfigJSONPath():
    return ServerConfig.path('localMemeStorageServer/storage/config.json')

def makeLocalMemeStorage():
    from apiutils.MemeStorageClasses.RepoLocalMemeStorage import RepoLocalMemeStorage
    return RepoLocalMemeStorage()


def getMemeFileName(id):
    for filename in os.listdir(getMemeDir()):
        if filename.startswith(f"meme_{id}"):
            return filename

    return None

def getMemeFileForID(cloudID):
    return join(getMemeDir(), getMemeFileName(cloudID))

def getMemeFileForURL(cloudURL):
    memeID = cloudURL.split('/')[-1]
    return getMemeFileForID(memeID)

def makeRemotelyAccessible(localURL):
    return localURL.replace('127.0.0.1', SYSTEM_IP)

def isLocalMemeURL(cloudURL):
    return ('127.0.0.1' in cloudURL) or (SYSTEM_IP in cloudURL)

def getLocalVersionForCloudMeme(cloudID:str, cloudURL:str, fileExt:str) -> tuple[str, str]:
    """
    Returns the local ID and local URL for a meme stored in the cloud service
    If the meme is already a local meme, then the ID and URL are returned unchanged
    If the meme does not exist in the local repository, it is downloaded from the cloudinary services
    :return tuple (local ID, local url)
    """
    if isLocalMemeURL(cloudURL):
        return cloudID, cloudURL

    cloudMapPath = ServerConfig.path('localMemeStorageServer', 'storage', 'cloudMap.json')
    with open(cloudMapPath, 'r') as file:
        cloudMap = json.load(file)

    if cloudID in cloudMap:
        return cloudMap[cloudID]['localID'], makeRemotelyAccessible(cloudMap[cloudID]['localURL'])

    print(f'Downloading {cloudID} to local repository ({cloudURL})')

    # download the meme from cloudinary
    resp = requests.get(cloudURL)
    if not resp.ok:
        raise Exception('Failed URL request!')

    uploader = makeLocalMemeStorage()
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

def cloudMemeNeedsToBeConvertedToLocal(cloudURL, ignoreEnv=False) -> bool:
    """
    Returns if the given item needs to be converted into its local version
    """
    # Only allowed if in development
    if ignoreEnv:
        return False

    if ServerConfig.isProdEnv():
        return False

    if ServerConfig.MEME_STORAGE != MemeStorageOption.LOCAL:
        return False

    if not cloudURL:
        return False

    # actual checking of the url
    return not isLocalMemeURL(cloudURL)
