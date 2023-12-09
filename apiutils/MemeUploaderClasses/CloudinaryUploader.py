import cloudinary
import cloudinary.uploader

from apiutils.MemeManagement.MemeUploaderInterface import MemeUploaderInterface
from apiutils.configs.ServerConfig import ServerConfig


class CloudinaryUploader(MemeUploaderInterface):
    def __init__(self):
        # Configure cloudinary
        cloudinary.config(
            cloud_name = ServerConfig.CLOUDINARY_CLOUD_NAME,
            api_key = ServerConfig.CLOUDINARY_API_KEY,
            api_secret = ServerConfig.CLOUDINARY_API_SECRET,
        )

    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        resp = cloudinary.uploader.upload(mediaBinary, unique_filename=False, overwrite=True)
        mediaID = str(resp['public_id'])
        deliveryURL = cloudinary.CloudinaryImage(mediaID).build_url()
        return mediaID, deliveryURL