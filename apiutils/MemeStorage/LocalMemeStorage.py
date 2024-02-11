import requests
from apiutils.MemeManagement.MemeStorageInterface import MemeStorageInterface, MemeStorageException

class LocalMemeStorage(MemeStorageInterface):
    """
    Communicates with local meme storage server running on port 5001
    """
    def __init__(self):
        pass

    def storageServer(self, route):
        return f'http://127.0.0.1:5001/{route}'

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