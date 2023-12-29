# import threading
import traceback

from flask import (Flask, redirect, request, url_for)
from flask_cors import CORS

from apiutils.HTTPResponses import *
from apiutils.MemeDBClasses.JSONMemeDB import JSONMemeDB
from apiutils.UploadSessionManager import UploadSessionManager
from apiutils.configs.ComponentOverrides import *

# Initialize our server config
ServerConfig.initConfig()
print('')
ServerConfig.printConfig()

# initialize app flask object
app = Flask(__name__)
CORS(app)


fileStorage = getServerFileStorage()
memeStorage = getServerMemeStorage()

JSONMemeDB.initSingleton(fileStorage)
memeDB = JSONMemeDB.getSingleton()

memeLib = MemeLibrary(memeDB, memeStorage)

if not memeLib.loadLibrary():
    raise Exception('There was an error loading the library!')

memeLib.indexLibrary()

def validAccess(req:request):
    accToken = req.headers.get('Access-Token')
    if accToken is None:
        return False
    return accToken in ServerConfig.ALLOWED_ACCESS_TOKENS

def saveLibrary() -> bool:
    """
    Saves the library to database
    :return:
    """
    return memeLib.saveLibrary()

def serverErrorResponse(e):
    return error_response(500, f"Unexpected Server Error")

@app.route('/download/<int:memeID>', methods=['GET'])
def route_download_meme(memeID):
    try:
        memeID = int(memeID)
        if not memeLib.hasMeme(memeID):
            return error_response(400, message=f"ID {memeID} does not exist in database")

        memeURL = memeLib.getMeme(memeID).getURL()
        return redirect(memeURL)
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)


@app.route('/info/<int:memeID>', methods=['GET'])
def route_info_meme(memeID):
    try:
        memeID = int(memeID)
        if not memeLib.hasMeme(memeID):
            return error_response(400, message=f"ID {memeID} does not exist in database")

        meme = memeLib.getMeme(memeID)
        memeJSON = {
            'id': meme.getID(),
            'name': meme.getName(),
            'type': meme.getTypeString(),
            'tags': meme.getTags(),
            'url': meme.getURL(),
        }

        return make_json_response(memeJSON)
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)


@app.route('/search', methods=['GET'])
def route_meme_search():
    try:
        query = request.args.get("query")

        if query is None or query == "":
            return error_response(400, 'No query found, use "query" for the URL parameter')

        itemsPerPage = request.args.get("per_page")
        pageNo = request.args.get("page")

        itemsPerPage = int(itemsPerPage) if itemsPerPage is not None else 10
        pageNo = int(pageNo) if pageNo is not None else 1

        matchedMemes = memeLib.findMemes(query, itemsPerPage=itemsPerPage, pageNo=pageNo)
        collated = [{
            'id': meme.getID(),
            'name': meme.getName(),
            'url': meme.getURL()}
            for meme in matchedMemes]

        return make_json_response({'results': collated, 'itemsPerPage': len(collated), 'pageNo': pageNo})
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)


@app.route('/browse', methods=['GET'])
def route_meme_browse():
    try:
        itemsPerPage = request.args.get("per_page")
        pageNo = request.args.get("page")

        if itemsPerPage is None:
            return error_response(400, '"per_page" is not included as a URL parameter')

        if pageNo is None:
            return error_response(400, '"page" is not included as a URL parameter')

        itemsPerPage = int(itemsPerPage)
        pageNo = int(pageNo)

        memes = memeLib.browseMemes(itemsPerPage, pageNo)
        collated = [{
            'id': meme.getID(),
            'name': meme.getName(),
            'url': meme.getURL()}
            for meme in memes]

        return make_json_response({'results': collated, 'itemsPerPage': itemsPerPage, 'pageNo': pageNo})
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)


@app.route('/edit/<int:memeID>', methods=['POST'])
def route_edit_meme(memeID):
    try:
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')

        memeID = int(memeID)
        if not memeLib.hasMeme(memeID):
            return error_response(400, message=f"ID {memeID} does not exist in database")

        name = request.json.get("name")
        tags = request.json.get("tags")

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

        if name is not None:
            if type(name) != str:
                return error_response(400, message=f"'name' parameter must be a JSON String")

        if tags is not None:
            if type(tags) != list:
                return error_response(400, message=f"'tags' parameter must be a JSON Array")

        # edit the meme
        memeLib.editMeme(memeID, name=name, tags=tags)

        # Save the changes to the library and reindex with new tags
        memeLib.saveLibrary()
        memeLib.indexLibrary()

        # return the meme information
        meme = memeLib.getMeme(memeID)
        memeJSON = {
            'id': meme.getID(),
            'name': meme.getName(),
            'type': meme.getTypeString(),
            'tags': meme.getTags(),
            'url': meme.getURL(),
        }

        return make_json_response(memeJSON)
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)


@app.route('/add', methods=['GET', 'POST'])
def route_add_new_meme():
    try:
        # Only people with valid access tokens are allowed
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')

        # Required keys are name:str, tags:str, fileExt:str
        requiredKeys = ["name", "tags", "fileExt"]
        if any(k not in request.json for k in requiredKeys):
            return error_response(400, 'Request is missing one or multiple keys')

        typesInfo = [
            ('name', request.json['name'], str, "String"),
            ('tags', request.json['tags'], list, "Array"),
            ('fileExt', request.json['fileExt'], str, "String")
        ]

        expectedTypeMsg = "name = JSON String, tags = JSON Array, fileExt = JSON String"

        for paramName, paramVal, paramType, msgType in typesInfo:
            if type(paramVal) != paramType:
                return error_response(400,
                                      message=f"'{paramName}' parameter must be a JSON {msgType}. Expected types are: {expectedTypeMsg}")

        # Create the entry in the database
        tags = [r.strip() for r in request.json['tags'].split(',')]
        meme = memeLib.addMemeToLibrary(name=request.json['name'], tags=tags, fileExt=request.json['fileExt'],
                                        addMemeToIndex=True)

        # respond with the item informaion and an upload URL
        return make_json_response(
            {
                "id": meme.getID(),
                "name": meme.getName(),
                'type': meme.getTypeString(),
                "tags": meme.getTags(),
                "fileExt": meme.getFileExt(),
                "uploadURL": url_for("route_upload_meme",
                                     uploadKey=UploadSessionManager.getInstance().newUploadKey(meme.getID()),
                                     _external=True),
            }
        )
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)


@app.route('/upload/<uploadKey>', methods=['GET', 'POST'])
def route_upload_meme(uploadKey):
    try:
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')

        uploadKey=str(uploadKey)

        sm = UploadSessionManager.getInstance()
        # check if there is an upload session for this key
        itemId = sm.getIDForKey(uploadKey)

        if itemId is None:
            return error_response(400, "Invalid upload session")

        if not memeLib.hasMeme(itemId):
            return error_response(400, "Invalid item ID")

        # valid upload session get the image data
        mediaBinary = request.data

        # make the upload here
        cloudURL = memeLib.uploadItemMedia(itemId, mediaBinary)

        # clear the upload session key
        sm.clearUploadKey(uploadKey)

        # TODO: Use thread to save and reindex library asynchronously
        # Meme library has index mutex to synchronize requests for searching or adding to the index
        # threading.Thread(target=saveLibrary).start()
        saveLibrary()

        return make_json_response({'url': cloudURL})

    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)

@app.route('/test')
def test():
    try:
        print(request.json)
        you = request.json.get('you')
        print(type(you) == list)
        raise Exception('Failure!')
        return make_json_response({'url': 'Hello'})
    except Exception as e:
        print(f'Exception Occured: {e}')
        traceback.print_exc()
        return serverErrorResponse(e)

# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Welcome To Meme Server, checkout the API usage: https://github.com/iffy-pi/reaction-meme-server?tab=readme-ov-file#using-the-api'})

# TODO: Add error handling for when library fails
# TODO: Implement Apple Shortcuts client API :D
# TODO: Make cloud ready, how are we handling this JSON file?
# TODO: Build the React client frontend :(((

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)