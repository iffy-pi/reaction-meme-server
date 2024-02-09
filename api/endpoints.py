from flask import (redirect, Response)
from typing import Union
from werkzeug.datastructures import FileStorage

from api.functions import makeMemeJSON
from apiutils.HTTPResponses import error_response, make_json_response
from apiutils.MemeManagement.MemeMediaType import MemeMediaType, memeMediaTypeToString, stringToMemeMediaType, \
    isValidMediaType
from apiutils.configs.ServerComponents import *

class EndPointException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def getMemeInfo(memeID: int,  memeLib: MemeLibrary) -> Response:
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    meme = memeLib.getMeme(memeID)
    return make_json_response(makeMemeJSON(meme))

def downloadMeme(memeID: int, memeLib: MemeLibrary) -> Response:
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    memeURL = memeLib.getMeme(memeID).getMediaURL()
    return redirect(memeURL)

def editMeme(memeID: int, name: Union[str, None], tags: Union[list[str], None], memeLib: MemeLibrary) -> Response:
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    # if no values to edit, just return the meme as it is
    if name is None and tags is None:
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

def browseMemes(itemsPerPage: int, pageNo: int, memeLib: MemeLibrary) -> Response:
    # TODO: Support media type filters?
    if itemsPerPage <= 0 or pageNo <= 0:
        return error_response(400, 'Invalid values for "page" and/or "per_page" parameters')

    memes = memeLib.browseMemes(itemsPerPage, pageNo)
    collated = [makeMemeJSON(meme) for meme in memes]

    return make_json_response({'results': collated, 'itemsPerPage': itemsPerPage, 'page': pageNo})


def searchMemes(query: str, itemsPerPage: Union[int, None], pageNo: Union[int, None], mediaTypeStr: Union[str, None], memeLib: MemeLibrary) -> Response:
    if query == "":
        return error_response(400, 'No query found, use "query" for the URL parameter')

    itemsPerPage = itemsPerPage if itemsPerPage is not None else 10
    pageNo = pageNo if pageNo is not None else 1

    if itemsPerPage <= 0 or pageNo <= 0:
        return error_response(400, 'Invalid values for "page" and/or "per_page" parameters')

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

    return make_json_response({'results': collated, 'itemsPerPage': itemsPerPage, 'page': pageNo})


def addNewMeme(name: str, tags: list, fileExt: str, mediaID: str, mediaURL: str, memeLib: MemeLibrary) -> Response:
    # Create the entry in the database
    meme = memeLib.addMemeToLibrary(name=name, tags=tags, fileExt=fileExt, mediaID=mediaID, mediaURL=mediaURL, addMemeToIndex=True)

    if meme is None:
        d = {
            'name': name, 'tags': tags, 'fileExt': fileExt, 'mediaID': mediaID, 'mediaURL': mediaURL
        }
        raise EndPointException(f'Failed to add meme to library: {d}')

    # TODO: Use thread to save and reindex library asynchronously
    # Meme library has index mutex to synchronize requests for searching or adding to the index
    # threading.Thread(target=saveLibrary).start()
    success = memeLib.saveLibrary()

    if not success:
        raise EndPointException('Failed to save the meme library')

    # respond with the item informaion and an upload URL
    return make_json_response(makeMemeJSON(meme))


def uploadMeme(fileExt: str, file: FileStorage, memeLib: MemeLibrary ) -> Response:
    if file.filename == '':
        return error_response(400, "No selected file")

    if not file:
        return error_response(400, "File is empty or does not exist")

    # Check the MIME Types
    if not isValidMediaType(fileExt):
        return error_response(400, f".{fileExt} is not an accepted file type")

    # Read the items and perform the upload
    fileBytes = file.stream.read()

    mediaID, mediaURL = memeLib.uploadMedia(fileBytes, fileExt)

    if mediaID is None or mediaURL is None:
        raise EndPointException('Failed to upload meme media')

    # return the ID and URL in the response
    return make_json_response(
        {
            "mediaID": mediaID,
            "mediaURL": mediaURL
        }
    )

# def uploadMemeRequest() -> Response:
#     # Create a new upload session key
#     sessionKey = UploadSessionManager.getInstance().newSession()
#     uploadUrl = url_for("route_upload_meme",
#                                      sessionKey=sessionKey,
#                                      _external=True)
#
#     return make_json_response({'uploadURL': uploadUrl})
#
# def uploadMeme(sessionKey:str, reqFiles, reqForm, memeLib: MemeLibrary ) -> Response:
#     um = UploadSessionManager.getInstance()
#     if not um.validSession(sessionKey):
#         return error_response(400, message=f"Invalid upload session")
#
#     if 'fileExt' not in reqForm:
#         return error_response(400, "Missing parameter: 'fileExt'")
#
#     if 'file' not in reqFiles:
#         return error_response(400, "No file property included in upload request")
#
#     file = reqFiles['file']
#
#     if file.filename == '':
#         return error_response(400, "No selected file")
#
#     if not file:
#         return error_response(400, "File is empty or does not exist")
#
#     fileExt = reqForm['fileExt']
#     fileBytes = file.stream.read()
#
#     # perform the upload
#     mediaID, mediaURL = memeLib.uploadMedia(fileBytes, fileExt)
#
#     if mediaID is None or mediaURL is None:
#         raise EndPointException('Failed to upload meme media')
#
#     # clear the session
#     um.clearSession(sessionKey)
#
#     # return the ID and URL in the response
#     return make_json_response(
#         {
#             "mediaID": mediaID,
#             "mediaURL": mediaURL
#         }
#     )