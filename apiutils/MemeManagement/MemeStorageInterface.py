class MemeStorageException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MemeStorageInterface:
    """
    Interface used by MemeLibrary to communicate with storage service used for memes
    That is, the service that actually stores the meme media.
    """
    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        """
        Upload the media binary to the storage service, returning the storage ID and delivery URL
        Returns None, None if the operation failed
        """
        raise Exception("Must implement in subclass")

    def getMedia(self, cloudID) -> bytes:
        """Returns the media bytes for the given cloud ID"""
        raise Exception("Must implement in subclass")

    def videoToThumbnail(self, cloudID) -> bytes:
        """
        Returns the bytes for a thumbnail image created from the video at the cloud ID
        Do not perform regular thumbnail compression since the image will be passed through a thumbnail maker
        """
        raise Exception("Must implement in subclass")