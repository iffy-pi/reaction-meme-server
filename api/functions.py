import traceback

from flask import request, Response

from apiutils.HTTPResponses import error_response
from apiutils.MemeDBClasses.JSONMemeDB import JSONMemeDB
from apiutils.MemeManagement.MemeContainer import MemeContainer
from apiutils.MemeManagement.MemeLibrary import MemeLibrary
from apiutils.configs.ComponentOverrides import getServerFileStorage, getServerMemeStorage
from apiutils.configs.ServerConfig import ServerConfig


def initAndIndexMemeLibrary() -> MemeLibrary:
    fileStorage = getServerFileStorage()
    memeStorage = getServerMemeStorage()

    JSONMemeDB.initSingleton(fileStorage)
    memeDB = JSONMemeDB.getSingleton()

    memeLib = MemeLibrary(memeDB, memeStorage)

    if not memeLib.loadLibrary():
        raise Exception('There was an error loading the library!')

    memeLib.indexLibrary()
    return memeLib

def validAccess(req:request) -> bool:
    accToken = req.headers.get('Access-Token')
    if accToken is None:
        return False
    return accToken in ServerConfig.ALLOWED_ACCESS_TOKENS

def makeMemeJSON(meme: MemeContainer) -> dict:
    return {
            'id': meme.getID(),
            'name': meme.getName(),
            'mediaType': meme.getMediaTypeString(),
            'fileExt': meme.getFileExt(),
            'tags': meme.getTags(),
            'url': meme.getURL(),
            'thumbnail': meme.getThumbnail()
        }


def serverErrorResponse(e: Exception) -> Response:
    print(f'Exception Occured: {e}')
    traceback.print_exc()
    return error_response(500, f"Unexpected Server Error")
