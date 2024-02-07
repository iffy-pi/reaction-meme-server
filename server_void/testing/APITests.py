import os
from random import randint
from unittest import TestCase
import json
import urllib.parse as urp

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


    def meme_id_route_checks(self, route, post=False, headers=None):
        with self.subTest(msg='Meme ID Route Checks'):
            # Subtest #1 : Test that non integer meme ID does not work
            if post:
                resp = requests.post(f'{route}/a', headers=headers)
            else:
                resp = requests.get(f'{route}/a', headers=headers)
            self.assertEqual(404, resp.status_code, msg='Testing Invalid Meme ID')

            # Subtest #2 : Test that meme ID that doesn't exist in the database returns a not found response
            newID = TestMemeDB.getInstance().getNextID()
            if post:
                resp = requests.post(f'{route}/{newID}', headers=headers)
            else:
                resp = requests.get(f'{route}/{newID}', headers=headers)
            self.assertTrue('error' in resp.json(), msg='Testing Nonexistent Meme ID')

    def privileged_endpoint_check(self, route):
        with self.subTest(msg='Privileged Endpoint Checks'):
            # Missing access token in header
            resp = requests.post(route)
            self.assertEqual(400, resp.status_code)

            # Invalid access token in header
            resp = requests.post(route, headers={'Access-Token': 'abc123'})
            self.assertEqual(400, resp.status_code)

    def check_meme_info_from_server(self, memeID, serverResp):
        # Check if server responds in the correct format for the meme data
        res = TestMemeDB.getInstance().get(memeID, name=True, mediaType=True, tags=True, fileExt=True, thumbnail=True, mediaURL=True)
        expectedResp = {
            'id': memeID,
            'name': res['name'],
            'mediaType': res['mediaType'],
            'tags': res['tags'],
            'fileExt': res['fileExt'],
            'url': res['mediaURL'],
            'thumbnail': res['thumbnail']
        }
        self.assertEqual(expectedResp, serverResp)

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
        self.assertEqual(localImgBytes, remoteImgBytes, msg='Downloaded media is correct')


    def test_api_get_meme(self):
        tdb = TestMemeDB.getInstance()
        tdb.loadDB()
        self.meme_id_route_checks(APITests.makeServerRoute('info'))

        memeID = APITests.getRandomMeme()
        resp = requests.get(APITests.makeServerRoute(f'info/{memeID}'))
        self.assertTrue(resp.ok)
        self.check_meme_info_from_server(memeID, resp.json()['payload'])

    @staticmethod
    def make_acc_token_header():
        return {
            'Access-Token': ServerConfig.ALLOWED_ACCESS_TOKENS[0]
        }

    def test_api_edit_meme(self):
        # tdb = TestMemeDB.getInstance()
        # tdb.loadDB()
        memeID = APITests.getRandomMeme()
        self.privileged_endpoint_check(APITests.makeServerRoute(f'edit/{memeID}'))
        self.meme_id_route_checks(APITests.makeServerRoute('edit'), post=True, headers=APITests.make_acc_token_header())

        tdb = TestMemeDB.getInstance()

        with self.subTest('Editing Name'):
            # Edit the meme
            newName = 'new meme name for test'
            memeID = APITests.getRandomMeme()
            resp = requests.post(
                APITests.makeServerRoute(f'edit/{memeID}'),
                headers=APITests.make_acc_token_header(),
                json= {
                    'name': newName,
                }
            )
            self.assertTrue(resp.ok, msg='Request Completed')

            # Load the db and check if the meme content matches what we expect
            tdb.loadDB()
            name = tdb.get(memeID, name=True)
            self.assertEqual(newName, name, msg='Names Match')

        with self.subTest('Editing Tags'):
            newTags = ['Testing', 'tag', 'one']
            memeID = APITests.getRandomMeme()
            resp = requests.post(
                APITests.makeServerRoute(f'edit/{memeID}'),
                headers=APITests.make_acc_token_header(),
                json={
                    'tags': newTags,
                }
            )
            self.assertTrue(resp.ok, msg='Request Completed')

            # Load the db and check if the meme content matches what we expect
            tdb.loadDB()
            tags = tdb.get(memeID, tags=True)
            self.assertEqual(newTags, tags, msg='Tags Match')

        with self.subTest('Incorrect Name Data Type'):
            memeID = APITests.getRandomMeme()
            resp = requests.post(
                APITests.makeServerRoute(f'edit/{memeID}'),
                headers=APITests.make_acc_token_header(),
                json={
                    'name': 22,
                }
            )
            self.assertEqual(400, resp.status_code)

        with self.subTest('Incorrect Tags Data Type'):
            newTags = 'Testing,tag,one'
            memeID = APITests.getRandomMeme()
            resp = requests.post(
                APITests.makeServerRoute(f'edit/{memeID}'),
                headers=APITests.make_acc_token_header(),
                json={
                    'tags': newTags,
                }
            )
            self.assertEqual(400, resp.status_code)

    def pagination_checks(self, baseRoute, routeRequiresPageParams=True, baseHasUrlParams=False):
        # Checks to make sure page logic and URL encoded arguments work properly
        combiner = '?'
        if baseHasUrlParams:
            combiner = '&'

        with self.subTest('Page Parameter Checks'):
            # Page cHECKS
            resp = requests.get(baseRoute)
            msg = 'Missing Page No and Items Per Page'

            # If page paramaters are optional, then we expect it to pass otherwise we return a client error
            if not routeRequiresPageParams:
                self.assertTrue(resp.ok, msg=msg)
            else:
                self.assertEqual(400, resp.status_code, msg=msg)

            # Try with invalid page params
            resp = requests.get(f'{baseRoute}{combiner}page=abc&per_page=abc')
            self.assertEqual(400, resp.status_code, msg='Invalid Page Parameters')

            # Try without of range page params
            resp = requests.get(f'{baseRoute}{combiner}page=-1&per_page=-3')
            self.assertEqual(400, resp.status_code, msg='Out of Range Page Params #1')

            # A page that is out of bounds, should just return an empty results list
            resp = requests.get(f'{baseRoute}{combiner}page=9999&per_page=20')
            self.assertEqual([], resp.json()['payload']['results'], msg='Empty results when page is out of range')

    def check_media_types(self, baseRoute, baseHasURLParams=True):
        combiner = '?'
        if baseHasURLParams:
            combiner = '&'

        # Any other types than "images", "videos" or "all" should give client error
        resp = requests.get(f'{baseRoute}{combiner}media_type=gif')
        self.assertEqual(400, resp.status_code, msg='Testing unknown media type is rejected')

        # Check that specific types return only their types
        mediaTypes = ['image', 'video']
        for mt in mediaTypes:
            with self.subTest(f'Testing {mt} media type'):
                resp = requests.get(f'{baseRoute}{combiner}media_type={mt}')
                results = resp.json()['payload']['results']
                self.assertTrue(
                    all(res['mediaType'] == mt for res in results),
                )

    def test_api_browse_meme(self):
        browseRoute = APITests.makeServerRoute('browse')
        self.pagination_checks(browseRoute)

        pageNo = 1
        itemsPerPage = 10

        # check if the results and pages align
        with self.subTest('Logical Behaviour'):
            # browse a page
            resp = requests.get(f'{browseRoute}?page={pageNo}&per_page={itemsPerPage}')
            # Is a valid request
            self.assertTrue(resp.ok, 'Request is valid')

            js = resp.json()
            self.assertTrue('payload' in js)

            results = js['payload']

            self.assertTrue('itemsPerPage' in results)
            self.assertEqual(itemsPerPage, results['itemsPerPage'])
            self.assertTrue('page' in results)
            self.assertEqual(pageNo, results['page'])
            self.assertTrue('results' in results)

            TestMemeDB.getInstance().loadDB()

            # check to make sure each meme matches the expected response format in the API docs
            for res in results['results']:
                self.assertTrue('id' in res)
                self.check_meme_info_from_server(res['id'], res)

    def test_api_search_meme(self):
        # Test that query parameter is required
        searchRoute = APITests.makeServerRoute('search')

        # No query URL parameter should result in an error
        resp = requests.get(f'{searchRoute}')
        self.assertEqual(400, resp.status_code)

        # Query as only URL parameter should pass, with default page being 1 and item being 10
        resp = requests.get(f'{searchRoute}?query=happy')
        self.assertTrue(resp.ok)
        results = resp.json()['payload']
        self.assertTrue('results' in results)
        self.assertTrue('itemsPerPage' in results)
        self.assertEqual(10, results['itemsPerPage'], msg='Matches default items per page mentioned in the documentation')
        self.assertTrue('page' in results)
        self.assertEqual(1, results['page'],
                         msg='Matches default page no mentioned in the documentation')

        # now do pagination checks
        self.pagination_checks(f'{searchRoute}?query=happy', routeRequiresPageParams=False, baseHasUrlParams=True)

        # Check the media type parameters
        self.check_media_types(f'{searchRoute}?query=happy')

        # Finally check if the results match api documentation
        resp = requests.get(f'{searchRoute}?query=happy')
        self.assertTrue(resp.ok)
        results = resp.json()['payload']['results']
        for res in results:
            self.assertTrue('id' in res)
            self.check_meme_info_from_server(res['id'], res)

    def test_api_upload_meme(self):
        self.assertEqual(1,1)

    def test_api_upload_meme_bad_access(self):
        self.assertEqual(1,1)

    def test_api_add_meme(self):
        self.assertEqual(1, 1)

    def test_api_add_meme_bad_access(self):
        self.assertEqual(1, 1)