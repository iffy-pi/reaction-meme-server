import os
import threading

from flask import (Flask, redirect, render_template, request, url_for)
from flask_cors import CORS

from apiutils.HTTPResponses import *
from apiutils.MemeDBClasses.JSONMemeDB import JSONMemeDB
from apiutils.UploadSessionManager import UploadSessionManager
from apiutils.configs.ComponentOverrides import *

# Initialize our server config
if os.environ.get('JSON_ENV') is not None:
    print('Loading Environment From JSON: '+ os.environ.get('JSON_ENV'))
    ServerConfig.setConfigFromJSON(os.environ.get('JSON_ENV'))
else:
    ServerConfig.setConfigFromEnv()

if ServerConfig.isDevEnv():
    print('Development environment is being used!')

# initialize app flask object
app = Flask(__name__)
CORS(app)


fileStorage = getServerFileStorage()
memeUploader = getServerMemeUploader()

JSONMemeDB.initSingleton(fileStorage)
memeDB = JSONMemeDB.getSingleton()

memeLib = MemeLibrary(memeDB, memeUploader)
loadLibrary(memeLib)

memeLib.indexLibrary()

def validAccess(req:request):
    accToken = req.headers.get('Access-Token')
    if accToken is None:
        return False
    if accToken not in ServerConfig.ALLOWED_ACCESS_TOKENS:
        return False
    return True

def saveAndReIndexLibrary():
    """
    Saves the library and reindexes, it will block index
    :return:
    """
    memeLib.saveLibrary()
    memeLib.indexLibrary()


@app.route('/memes/download/<int:memeID>', methods=['GET'])
def route_get_meme(memeID):
    memeID = int(memeID)
    if not memeLib.hasMeme(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    memeURL = memeLib.getMeme(memeID).getURL()
    return redirect(memeURL)


@app.route('/memes/search', methods=['GET'])
def route_meme_search():
    query = request.args.get("query")

    if query is None or query == "":
        return error_response(400, 'No query found, use "query" for the URL parameter')

    itemsPerPage = request.args.get("per_page")
    pageNo = request.args.get("page")

    itemsPerPage = int(itemsPerPage) if itemsPerPage is not None else 10
    pageNo = int(pageNo) if pageNo is not None else 1

    matchedMemes = memeLib.findMemes(query, itemsPerPage=itemsPerPage, pageNo=pageNo)
    collated = [ {
        'id': meme.getID(),
        'name': meme.getName(),
        'url': meme.getURL() }
    for meme in matchedMemes]

    return make_json_response({ 'results' : collated, 'itemsPerPage': itemsPerPage, 'pageNo' : pageNo})

@app.route('/memes/browse', methods=['GET'])
def route_meme_browse():
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

    return make_json_response({'results': collated, 'itemsPerPage': itemsPerPage, 'pageNo' : pageNo})

@app.route('/memes/add', methods=['GET', 'POST'])
def route_add_new_meme():
    # Only people with valid access tokens are allowed
    if not validAccess(request):
        return error_response(400, 'Invalid Access Token')

    # Required keys are name:str, tags:str, fileExt:str
    requiredKeys = ["name", "tags", "fileExt"]
    if any(k not in request.json for k in requiredKeys):
        return error_response(400, 'Request is missing one or multiple keys')

    # Create the entry in the database
    tags = [ r.strip() for r in request.json['tags'].split(',')]
    meme = memeLib.makeMemeAndAddToLibrary(name=request.json['name'], tags=tags, fileExt=request.json['fileExt'])

    # respond with the item informaion and an upload URL
    return make_json_response(
        {
            "id": meme.getID(),
            "name": meme.getName(),
            "tags" : meme.getTags(),
            "fileExt": meme.getFileExt(),
            "uploadURL": url_for("upload_meme", uploadKey=UploadSessionManager.getInstance().newUploadKey(meme.getID()), _external=True),
        }
    )


@app.route('/memes/upload/<uploadKey>', methods=['GET', 'POST'])
def upload_meme(uploadKey):
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

    # Use thread to save and reindex library asynchronously
    # Meme library has index mutex to synchronize requests for searching or adding to the index
    threading.Thread(target=saveAndReIndexLibrary).start()
    return make_json_response({'url': cloudURL})

# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Hello World'})

# TODO: Implement Apple Shortcuts client API :D
# TODO: Make cloud ready, how are we handling this JSON file?
# TODO: Build the React client frontend :(((
# TODO: Tag the remaining 400 memes

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)