class MemeUploaderInterface:
    """
    Interface used by MemeLibrary to upload memes to hosting service.
    """
    def __init__(self):
        pass

    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        """
        Upload the media binary to the cloud, returning the cloud ID and cloud URL
        """
        raise Exception("Must implement in subclass")