import json
import os

import requests

from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from apiutils.FileStorageClasses.RepoLocalFileStorage import RepoLocalFileStorage
from apiutils.MemeDBClasses.JSONMemeDB import JSONMemeDB
from apiutils.configs.ServerConfig import ServerConfig
from localMemeStorageServer.utils.LocalStorageUtils import makeLocalMemeStorage

def getServerName(serverIden):
    # make request
    res = requests.get('https://api.pushbullet.com/v2/devices',
                       headers={'Access-Token': ServerConfig.PBFS_ACCESS_TOKEN})
    devices = res.json()['devices']
    foundNames = [ d['nickname'] for d in devices if d['iden'] == serverIden]
    if len(foundNames) < 1:
        raise Exception('No identifier found!')

    return foundNames[0]
def uploadLocalJSONDBToPBFS(serverIdentifier:str = ServerConfig.PBFS_SERVER_IDENTIFIER):
    """
    Saves data/db.json into PBFS so it matches
    """
    print('This will upload the current version of data/db.json as the new CLOUD JSON file')
    print(f'Uploading to server: {getServerName(serverIdentifier)}')
    res = input('Are you SURE you want to do this? (y/n): ').strip().lower()
    if res != 'y':
        print('Exited!')
        return

    pbfs = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, serverIdentifier)
    lcfs = RepoLocalFileStorage()
    db = lcfs.getJSONDB()
    print('Writing data/db.json')
    pbfs.writeJSONDB(db)
    print('Done')

def downloadPBFSJSONDBToLocal(serverIdentifier:str = ServerConfig.PBFS_SERVER_IDENTIFIER):
    """
    Downloads the JSON db file from PBFS and saves it into local db
    """
    print(f'Downloading from server: {getServerName(serverIdentifier)}')
    res = input('Are you SURE you want to do this? (y/n): ').strip().lower()
    if res != 'y':
        print('Exited!')
        return
    pbfs = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, serverIdentifier)
    lcfs = RepoLocalFileStorage()
    db = pbfs.getJSONDB()
    lcfs.writeJSONDB(db)

def downloadNewMemesFromCloud(jsonDB:JSONMemeDB):
    cloudMapPath = ServerConfig.path('localMemeStorageServer', 'storage', 'cloudMap.json')
    jsonDB.loadDB()

    with open(cloudMapPath, 'r') as file:
        cloudMap = json.load(file)

    for meme in jsonDB.getAllDBMemes():
        cloudID = meme.getMediaID(autoConvertToLocal=False)
        cloudURL = meme.getMediaURL(autoConvertToLocal=False)

        if cloudID is None:
            continue
        if cloudID in cloudMap:
            continue

        print(f'Downloading Meme #{meme.getID()}, CloudID={cloudID} to local repository ({cloudURL})')

        # download the meme from cloudinary
        resp = requests.get('http://res.cloudinary.com/du6q7wdat/image/upload/v1/memes/kyxdqozu9587bgy7h75e')
        if not resp.ok:
            raise Exception('Failed URL request!')

        uploader = makeLocalMemeStorage()
        localID, localURL = uploader.uploadMedia(resp.content, meme.getFileExt())

        # update the cloud map with the new info
        cloudMap[cloudID] = {
            'cloudID': cloudID,
            'cloudURL': cloudURL,
            'localID': localID,
            'localURL': localURL
        }

    with open(cloudMapPath, 'w') as file:
        json.dump(cloudMap, file, indent=4)

    print('Local Cloud Map Updated!')

def matchLocalEnvToProd(prodServerIden:str):
    """
    Makes the local JSON DB and local meme storage match the production JSON DB and the memes in the cloud storage
    Does this by downloading the JSON db from PushBullet
    And downloaidng the new memes from cloud
    """
    print('Downloading DB...')
    downloadPBFSJSONDBToLocal(serverIdentifier=prodServerIden)
    print('Downloading New Cloud Memes...')
    downloadNewMemesFromCloud(JSONMemeDB(RepoLocalFileStorage()))
    print('Completed')
