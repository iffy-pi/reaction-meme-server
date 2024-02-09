import requests
from apiutils.MemeManagement.MemeStorageInterface import MemeStorageInterface, MemeStorageException

class RepoLocalMemeStorage(MemeStorageInterface):
    """
    Stores memes for use by localMemeStorageServer
    Specifically stored under localMemeStorageServer/storage/memes
    """
    def __init__(self):
        """
        The class works in the following way:
            The config file is used to keep track of the next ID to assign to a newly uploaded meme
            When a new meme is uploaded, it is written to the memeDir with the naming format meme_{id}.{fileExt} (or with uploaded appended as mentioned above)
            The config file is also updated when a new meme is added, the value of next ID is incremented.
        """
        pass

    def storageServer(self, route):
        return f'http://192.168.2.101:5001/{route}'

    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        resp = requests.post(self.storageServer(f'local/upload?fileExt={fileExt}'), data=mediaBinary)
        if not resp.ok:
            raise MemeStorageException('Local storage server failed!')

        res = resp.json()
        return res['payload']['mediaID'], res['payload']['mediaURL']

    def getMedia(self, mediaID) -> bytes:
        resp = requests.get(self.storageServer(f'local/meme/{mediaID}'))
        if not resp.ok:
            raise MemeStorageException('Local storage server failed!')
        return resp.content

    def videoToThumbnail(self, mediaID) -> bytes:
        resp = requests.get(self.storageServer(f'local/thumbnail/{mediaID}'))
        if not resp.ok:
            raise MemeStorageException('Local storage server failed!')
        return resp.content