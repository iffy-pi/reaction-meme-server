import cloudinary
import cloudinary.uploader
from apiutils.MediaDB_File_Servers.MediaDBFileServer import MediaDBFileServer
import os
import uuid

CLOUD_NAME = os.environ.get('RMSVR_CLOUDINARY_CLOUD_NAME') 
API_KEY = os.environ.get('RMSVR_CLOUDINARY_API_KEY')
API_SECRET = os.environ.get('RMSVR_CLOUDINARY_API_SECRET')

class MediaDB:
    def __init__(self, fileServer:MediaDBFileServer, dbIndex=None, testing=False):
        """
        Class to manage database of reaction memes, will handle the loading, reading and writing of the JSON db file
        """
        self.__db = None
        self.__fileServer = fileServer
        self.testing = testing

        cloudinary.config(
            cloud_name = CLOUD_NAME,
            api_key = API_KEY,
            api_secret = API_SECRET,
        )

    def __del__(self):
        # Writes the json file away
        pass

    def initDB(self):
        self.__db = {
            'elementCount': 0,
            'elements': {}
        }

    def loadDB(self):
        self.__db = self.__fileServer.loadDBFromJSON()

    def updateDB(self):
        self.__fileServer.writeJSONDB(self.__db)

    def getByID(self, mediaID: str):
        if mediaID not in self.__db['elements']:
            return None
        
        return self.__db[mediaID]

    def __addElementToDB(self, name, fileExt, tags, cloudinaryID, cloudinaryURL):
        elemId = self.__db['elementCount']
        self.__db['elements'][elemId] = {
            'id': elemId,
            'name': name,
            'fileExt': fileExt,
            'tags': tags,
            'cloudinaryID': cloudinaryID,
            'cloudinaryURL': cloudinaryURL
        }
        self.__db['elementCount'] += 1
    
    def addMedia(self, mediaBinary, name, fileExt, tags):
        # upload to cloudinary
        cloudId, cloudURL = self.uploadMediaToCloudinary(mediaBinary, fileExt)

        # add to DB
        self.__addElementToDB(name, fileExt, tags, cloudId, cloudURL)

    def addMediaFrom(self, filePath, name, tags):
        # first upload the file to cloudinary
        with open(filePath, 'rb') as file:
            mediaBinary = file.read()
        self.addMedia(mediaBinary, name, os.path.splitext(filePath)[1].replace('.', ''), tags)

    def __mockUploader(self, mediaBinary, fileExt):
        # saves them to local location
        mockLocation = "C:\\local\\GitRepos\\reaction-meme-server\\mockCloudinary"
        fileId = str(uuid.uuid4())
        filePath = os.path.join(mockLocation, f'{fileId}.{fileExt}')
        with open( filePath, 'wb') as file:
            file.write(mediaBinary)

        return fileId, filePath

    def __realUploader(self, mediaBinary):
        # Actually uploads the files to cloudinary
        resp = cloudinary.uploader.upload(mediaBinary, unique_filename=False, overwrite=True)
        mediaID = resp['public_id']
        deliveryURL = cloudinary.CloudinaryImage(mediaID).build_url()
        return mediaID, deliveryURL

    def uploadMediaToCloudinary(self, mediaBinary, fileExt):
        """
        Uploads the binary to cloudinary and returns the URL for delivery
        """
        if self.testing:
            return self.__mockUploader(mediaBinary, fileExt)
        else:
            return self.__realUploader(mediaBinary)





