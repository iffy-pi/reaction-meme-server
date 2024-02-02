import os
from random import randint
from unittest import TestCase
import json

import requests

from apiutils.configs.ServerConfig import ServerConfig
from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from server_void.testing.test_funcs import makeServerRoute

from localMemeStorageServer.utils.LocalStorageUtils import makeLocalMemeStorage, getLocalVersionForCloudMeme
from server_void.testing.TestMemeDB import TestMemeDB



class APITests(TestCase):
    """
    API Testing, implemented according to API specification in README.
    """
    @classmethod
    def setUpClass(cls):
        # Download latest production db and apply it to the test db
        print('Downloading Prod DB into testing....')
        ServerConfig.setConfigFromJSON(ServerConfig.path('devenv', 'config_jsons', 'prodenv.json'))
        pbfs = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)
        with open(ServerConfig.path('data', 'testing_db.json'), 'w') as file:
            json.dump(pbfs.getJSONDB(), file, indent=4)
        print('Done')
        ServerConfig.setConfigFromJSON(ServerConfig.path('devenv/config_jsons/testenv.json'))
        input('Run "local meme storage" configuration. Press Enter when this is done')
        input('Run "api(test)" configuration. Press Enter when this is done')

    def test_download_meme(self):
        # Get random meme ID
        tdb = TestMemeDB.getInstance()
        tdb.loadDB()
        itemIds = list(tdb.getItems().keys())
        memeID = randint(0, len(itemIds)-1)

        # Get the meme mediaID
        res = tdb.get(memeID, mediaID=True, mediaURL=True, fileExt=True)
        localMediaID, _ = getLocalVersionForCloudMeme(res['mediaID'], res['mediaURL'], res['fileExt'])

        # Get the bytes for the local version
        localStorage = makeLocalMemeStorage()
        localImgBytes = localStorage.getMedia(localMediaID)

        # Get the bytes for the remote version
        resp = requests.get(makeServerRoute(f'download/{memeID}'))
        remoteImgBytes = resp.content

        self.assertEqual(localImgBytes, remoteImgBytes)

    def test_get_meme(self):
        self.assertEqual(1, 1)

    def test_edit_meme(self):
        self.assertEqual(1, 1)

    def test_edit_meme_bad_access(self):
        self.assertEqual(1, 1)

    def test_edit_meme_bad_data(self):
        self.assertEqual(1, 1)

    def test_search_meme(self):
        self.assertEqual(1, 1)

    def test_browse_meme(self):
        self.assertEqual(1, 1)

    def test_upload_meme(self):
        self.assertEqual(1,1)

    def test_upload_meme_bad_access(self):
        self.assertEqual(1,1)

    def test_add_meme(self):
        self.assertEqual(1, 1)

    def test_add_meme_bad_access(self):
        self.assertEqual(1, 1)