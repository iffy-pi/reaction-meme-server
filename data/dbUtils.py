import json
import os

from apiutils.MemeUploaderClasses.CloudinaryUploader import CloudinaryUploader
from apiutils.configs.ServerConfig import ServerConfig
from localMemeStorageServer.utils.storageServerUtils import getMemeFileName, getMemeDir


def uploadLocalMemeToCloudinary(clUploader:CloudinaryUploader, memeId:int):
    # Uploads the given meme from the local storage server to cloudinary
    # Returning the new id and delivery URL
    filename = getMemeFileName(memeId)
    if filename is None:
        raise Exception(f'Could not find meme for ID: {memeId}')

    filePath = os.path.join(getMemeDir(), filename)

    if not os.path.exists(filePath):
        raise Exception(f'Path "{filePath} does not exist!')

    fileExt = os.path.splitext(filename)[1].lower().replace('.', '')
    with open(filePath, "rb") as file:
        mediaBinary = file.read()

    cloudId, cloudURL = clUploader.uploadMedia(mediaBinary, fileExt)
    return cloudId, cloudURL


def uploadMemesToCloudinary():
    clu = CloudinaryUploader()

    oldDBFile = os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'db.json')
    newDBFile = os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'newDB.json')

    loadPath = oldDBFile
    if os.path.exists(newDBFile):
        loadPath = newDBFile

    # open the db file
    with open(loadPath, "r") as file:
        db = json.load(file)


    def saveDB():
        with open(newDBFile, "w") as f:
            json.dump(db, f, indent=4)

    for i, item in enumerate(db['items'].values()):
        # get the meme id
        memeId = item['cloudID']

        # do the upload
        cloudID, cloudURL = uploadLocalMemeToCloudinary(clu, memeId)

        # Update the fields in the db
        item['cloudID'] = cloudID
        item['cloudURL'] = cloudURL

        # save the new db
        saveDB()

        # print status
        print('Uploaded {}, Cloud URL: {}'.format(item['id'], cloudURL))