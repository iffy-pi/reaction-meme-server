import cloudinary
import cloudinary.uploader
import requests

from apiutils.MemeManagement.MemeStorageInterface import MemeStorageInterface
from apiutils.configs.ServerConfig import ServerConfig


class CloudinaryMemeStorage(MemeStorageInterface):
    def __init__(self):
        # Configure cloudinary
        cloudinary.config(
            cloud_name = ServerConfig.CLOUDINARY_CLOUD_NAME,
            api_key = ServerConfig.CLOUDINARY_API_KEY,
            api_secret = ServerConfig.CLOUDINARY_API_SECRET,
        )

    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        resp = cloudinary.uploader.upload(mediaBinary, folder="memes", resource_type="auto")
        if 'public_id' not in resp:
            return None, None

        mediaID = str(resp['public_id'])
        deliveryURL = cloudinary.utils.cloudinary_url(mediaID, resource_type=resp['resource_type'])[0]
        return mediaID, deliveryURL

    def getMedia(self, cloudID) -> bytes:
        url = cloudinary.utils.cloudinary_url(cloudID)[0]
        resp = requests.get(url)
        return resp.content

    def videoToThumbnail(self, cloudID) -> bytes:
        url = cloudinary.CloudinaryVideo(cloudID).video_thumbnail(start_offset=0)
        resp = requests.get(url)
        return resp.content