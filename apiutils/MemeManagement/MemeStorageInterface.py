class MemeStorageInterface:
    """
    Interface used by MemeLibrary to communicate with storage service used for memes
    That is, the service that actually stores the meme media.
    """
    def __init__(self):
        pass

    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        """
        Upload the media binary to the storage service, returning the storage ID and delivery URL
        """
        raise Exception("Must implement in subclass")