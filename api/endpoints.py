from flask import (redirect, Response, url_for)

from api.functions import makeMemeJSON
from apiutils.HTTPResponses import error_response, make_json_response
from apiutils.MemeManagement.MemeMediaType import MemeMediaType, memeMediaTypeToString, stringToMemeMediaType
from apiutils.UploadSessionManager import UploadSessionManager
from apiutils.configs.ComponentOverrides import *

class EndPointException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def getMemeInfo(memeID,  memeLib: MemeLibrary) -> Response:
    memeID = int(memeID)
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    meme = memeLib.getMeme(memeID)
    return make_json_response(makeMemeJSON(meme))

def downloadMeme(memeID, memeLib: MemeLibrary) -> Response:
    memeID = int(memeID)
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    memeURL = memeLib.getMeme(memeID).getURL()
    return redirect(memeURL)

def editMeme(memeID, name, tags, memeLib: MemeLibrary) -> Response:
    memeID = int(memeID)
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    typesInfo = [
        ('name', name, str, "String"),
        ('tags', tags, list, "Array"),
    ]

    expectedTypeMsg = "name = JSON String, tags = JSON Array"

    for paramName, paramVal, paramType, msgType in typesInfo:
        if paramVal is None:
            continue

        if type(paramVal) != paramType:
            return error_response(400,
                                  message=f"'{paramName}' parameter must be a JSON {msgType}. Expected types are: {expectedTypeMsg}")

    # if no values to edit, just return the meme as it is
    if all(param is None for param in [name, tags]):
        meme = memeLib.getMeme(memeID)
        return make_json_response(makeMemeJSON(meme))

    # edit the meme
    if not memeLib.editMeme(memeID, name=name, tags=tags):
        raise EndPointException(f'Failed to edit meme in the library, id={memeID}, name="{name}", tags={tags}')

    # Save the changes to the library and reindex with new tags
    if not memeLib.saveLibrary():
        raise EndPointException('Failed to save the meme library')

    memeLib.indexLibrary()

    # return the meme information
    meme = memeLib.getMeme(memeID)
    return make_json_response(makeMemeJSON(meme))

def browseMemes(itemsPerPage, pageNo, memeLib: MemeLibrary) -> Response:
    # TODO: Support media type filters?
    if itemsPerPage is None:
        return error_response(400, '"per_page" is not included as a URL parameter')

    if pageNo is None:
        return error_response(400, '"page" is not included as a URL parameter')

    itemsPerPage = int(itemsPerPage)
    pageNo = int(pageNo)

    memes = memeLib.browseMemes(itemsPerPage, pageNo)
    collated = [makeMemeJSON(meme) for meme in memes]

    return make_json_response({'results': collated, 'itemsPerPage': itemsPerPage, 'pageNo': pageNo})


def searchMemes(query, itemsPerPage, pageNo, mediaTypeStr, memeLib: MemeLibrary) -> Response:
    if query is None or query == "":
        return error_response(400, 'No query found, use "query" for the URL parameter')

    itemsPerPage = int(itemsPerPage) if itemsPerPage is not None else 10
    pageNo = int(pageNo) if pageNo is not None else 1
    mediaType = None

    if mediaTypeStr is not None:
        mediaTypeStr = mediaTypeStr.lower()
        acceptedTypeStrs = ["all", memeMediaTypeToString(MemeMediaType.IMAGE), memeMediaTypeToString(MemeMediaType.VIDEO)]
        if mediaTypeStr not in acceptedTypeStrs:
            return error_response(400, f'Invalid media type: "{mediaTypeStr}". Accepted types are: {acceptedTypeStrs}')

        if mediaTypeStr != "all":
            mediaType = stringToMemeMediaType(mediaTypeStr)

    matchedMemes = memeLib.search(query, itemsPerPage=itemsPerPage, pageNo=pageNo, onlyMediaType=mediaType)
    collated = [makeMemeJSON(meme) for meme in matchedMemes]

    return make_json_response({'results': collated, 'itemCount': len(collated), 'pageNo': pageNo})


def addNewMeme(name, tags, fileExt, cloudID, cloudURL, memeLib: MemeLibrary) -> Response:
    typesInfo = [
        ('name', name, str, "String"),
        ('tags', tags, list, "Array"),
        ('fileExt', fileExt, str, "String"),
        ('cloudID', cloudID, str, "String"),
        ('cloudURL', cloudURL, str, "String")
    ]

    expectedTypeMsg = "name: String, tags: Array, fileExt: String, cloudID: String, cloudURL: str"

    for paramName, paramVal, paramType, msgType in typesInfo:
        if paramVal is None:
            return error_response(400,
                                  message=f"'{paramName}' parameter is missing.")

        if type(paramVal) != paramType:
            return error_response(400,
                                  message=f"'{paramName}' parameter must be a JSON {msgType}. Expected types are: {expectedTypeMsg}")

    # Create the entry in the database
    meme = memeLib.addMemeToLibrary(name=name, tags=tags, fileExt=fileExt, cloudID=cloudID, cloudURL=cloudURL, addMemeToIndex=True)

    if meme is None:
        d = {
            'name': name, 'tags': tags, 'fileExt': fileExt, 'cloudID': cloudID, 'cloudURL': cloudURL
        }
        raise EndPointException(f'Failed to add meme to library: {d}')

    # TODO: Use thread to save and reindex library asynchronously
    # Meme library has index mutex to synchronize requests for searching or adding to the index
    # threading.Thread(target=saveLibrary).start()
    success = memeLib.saveLibrary()

    if not success:
        raise EndPointException('Failed to save the meme library')

    # respond with the item informaion and an upload URL
    return make_json_response(
        {
            "id": meme.getID(),
            "name": meme.getName(),
            "mediaType": meme.getMediaTypeString(),
            "tags": meme.getTags(),
            "fileExt": meme.getFileExt(),
            "url" : meme.getURL()
        }
    )


def uploadMemeRequest(fileExt) -> Response:
    if fileExt is None:
        return error_response(400, 'Missing parameter "fileExt"')

    # Create a new upload session key
    sessionKey = UploadSessionManager.getInstance().newSession(fileExt=fileExt)
    uploadUrl = url_for("route_upload_meme",
                                     sessionKey=sessionKey,
                                     _external=True)

    return make_json_response({'uploadURL': uploadUrl})


def uploadMeme(sessionKey:str, data:bytes, memeLib: MemeLibrary ) -> Response:
    um = UploadSessionManager.getInstance()
    if not um.validSession(sessionKey):
        return error_response(400, message=f"Invalid upload session")

    # get the file extension
    fileExt = um.getSessionData(sessionKey)['fileExt']

    # perform the upload
    cloudID, cloudURL = memeLib.uploadMedia(data, fileExt)

    if cloudID is None or cloudURL is None:
        raise EndPointException('Failed to upload meme media')

    # clear the session
    um.clearSession(sessionKey)

    # return the ID and URL in the response
    return make_json_response(
        {
            "cloudID": cloudID,
            "cloudURL": cloudURL
        }
    )