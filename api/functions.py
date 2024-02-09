import traceback

from flask import request, Response

from apiutils.HTTPResponses import error_response
from apiutils.MemeDBClasses.JSONMemeDB import JSONMemeDB
from apiutils.MemeManagement.MemeContainer import MemeContainer
from apiutils.MemeManagement.MemeLibrary import MemeLibrary
from apiutils.configs.ServerComponents import getServerFileStorage, getServerMemeStorage
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
            'url': meme.getMediaURL(),
            'thumbnail': meme.getThumbnail()
        }


def serverErrorResponse(e: Exception) -> Response:
    print(f'Exception Occured: {e}')
    traceback.print_exc()
    return error_response(500, f"Unexpected Server Error")

def checkDictionaryParams(dix: dict, paramInfo: list[tuple]) -> tuple[bool, str]:
    """
    Parameter info is a list of tuples, where each tuple is:
    ( <key in dictionary>, <boolean if required>, <expected type>)
    Returns tuple:
        boolean - If all parameters pass
        str - Error message, None if all the parameters pass
    """
    pythonToJSONTypes = {
        int: 'Number',
        str: 'String',
        list: 'Array',
        float: 'Number',
        dict: 'Dictionary'
    }

    typeMsgList = []
    for paramKey, required, expectedType in paramInfo:
        typeMsgList.append('{}{} = {}'.format(
            '(Optional) ' if not required else '',
            paramKey,
            pythonToJSONTypes[expectedType],
        ))

    typeMsg = ', '.join(typeMsgList)
    typeMsg = f'Expected Types: {typeMsg}'

    for paramKey, required, expectedType in paramInfo:
        # Check if the key exists
        paramVal = dix.get(paramKey)
        if paramVal is None:
            if not required:
                continue

            message = f'"{paramKey}" is missing. {typeMsg}'
            return False, message

        # Check its data type
        if type(paramVal) != expectedType:
            message = f'"{paramKey}" must be a {pythonToJSONTypes[expectedType]}. {typeMsg}'
            return False, message

    return True, ''

def checkReqJSONParameters(req:request, paramInfo:list[tuple]) -> tuple[bool, str]:
    if not req.is_json:
        return False, 'JSON content is missing from request'

    return checkDictionaryParams(request.json, paramInfo)

