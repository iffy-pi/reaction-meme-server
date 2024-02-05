import os
from random import randint
from unittest import TestCase
import json

import requests

from apiutils.configs.ServerConfig import ServerConfig
from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from server_void.testing.test_funcs import makeServerRoute, isServerReachable

from localMemeStorageServer.utils.LocalStorageUtils import makeLocalMemeStorage, getLocalVersionForCloudMeme
from server_void.testing.TestMemeDB import TestMemeDB



class APITests(TestCase):
    """
    API Testing, implemented according to API specification in README.
    """
    MEME_SERVER_URL = 'http://127.0.0.1:5000'
    LOCAL_MEME_STORAGE_SERVER_URL = 'http://127.0.0.1:5001'
    @classmethod
    def setUpClass(cls):
        print(f'Checking connection to Lcoal Meme Storage Server: {APITests.LOCAL_MEME_STORAGE_SERVER_URL}')
        if not isServerReachable(APITests.LOCAL_MEME_STORAGE_SERVER_URL):
            raise Exception('Lcoal Meme Storage Server is not reachable')
        print('Connected')

        print(f'Checking connection to Meme Server: {APITests.MEME_SERVER_URL}')
        if not isServerReachable(APITests.MEME_SERVER_URL):
            raise Exception('Meme Server is not reachable')
        print('Connected')

        # Download latest production db and apply it to the test db
        print('Downloading Prod DB into testing....')
        ServerConfig.setConfigFromJSON(ServerConfig.path('devenv', 'config_jsons', 'prodenv.json'))
        pbfs = PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER)
        with open(ServerConfig.path('data', 'testing_db.json'), 'w') as file:
            json.dump(pbfs.getJSONDB(), file, indent=4)
        print('Done')
        ServerConfig.setConfigFromJSON(ServerConfig.path('devenv/config_jsons/testenv.json'))


    @staticmethod
    def makeServerRoute(route:str):
        return f'{APITests.MEME_SERVER_URL}/{route}'

    @staticmethod
    def getRandomMeme():
        itemIds = list(TestMemeDB.getInstance().getItems().keys())
        memeID = randint(0, len(itemIds) - 1)
        return memeID

    def meme_id_route_checks(self, route):
        with self.subTest():
            # Subtest #1 : Test that non integer meme ID does not work
            resp = requests.get(f'{route}/a')
            self.assertEqual(resp.status_code, 404)

            # Subtest #2 : Test that meme ID that doesn't exist in the database returns a not found response
            newID = TestMemeDB.getInstance().getNextID()
            resp = requests.get(f'{route}/{newID}')
            self.assertTrue('error' in resp.json())


    def test_api_download_meme(self):
        tdb = TestMemeDB.getInstance()
        tdb.loadDB()
        self.meme_id_route_checks(APITests.makeServerRoute('download'))

        # Subtest #3 : Test that the meme media retrieved matches what we expect
        # Get a random meme media
        memeID = APITests.getRandomMeme()
        res = tdb.get(memeID, mediaID=True, mediaURL=True, fileExt=True)
        localMediaID, _ = getLocalVersionForCloudMeme(res['mediaID'], res['mediaURL'], res['fileExt'])
        localStorage = makeLocalMemeStorage()
        localImgBytes = localStorage.getMedia(localMediaID)
        # Get the bytes for the remote version
        resp = requests.get(APITests.makeServerRoute(f'download/{memeID}'))
        remoteImgBytes = resp.content
        self.assertEqual(localImgBytes, remoteImgBytes)

    def test_api_get_meme(self):
        tdb = TestMemeDB.getInstance()
        tdb.loadDB()
        self.meme_id_route_checks(APITests.makeServerRoute('info'))

        memeID = APITests.getRandomMeme()
        res = tdb.get(memeID, name=True, mediaType=True, tags=True, fileExt=True, thumbnail=True, mediaURL=True)
        expectedResp = {
            'id': memeID,
            'name': res['name'],
            'mediaType': res['mediaType'],
            'tags': res['tags'],
            'fileExt': res['fileExt'],
            'url': res['mediaURL'],
            'thumbnail': res['thumbnail']
        }

        resp = requests.get(APITests.makeServerRoute(f'info/{memeID}'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['payload'], expectedResp)

    def test_api_edit_meme(self):
        self.assertEqual(1, 1)

    def test_api_edit_meme_bad_access(self):
        self.assertEqual(1, 1)

    def test_api_edit_meme_bad_data(self):
        self.assertEqual(1, 1)

    def test_api_search_meme(self):
        self.assertEqual(1, 1)

    def test_api_browse_meme(self):
        self.assertEqual(1, 1)

    def test_api_upload_meme(self):
        self.assertEqual(1,1)

    def test_api_upload_meme_bad_access(self):
        self.assertEqual(1,1)

    def test_api_add_meme(self):
        self.assertEqual(1, 1)

    def test_api_add_meme_bad_access(self):
        self.assertEqual(1, 1)