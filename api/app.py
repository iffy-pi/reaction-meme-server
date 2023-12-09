import os
import threading

from flask import (Flask, redirect, render_template, request, url_for)
from flask_cors import CORS

from apiutils.FileStorageClasses.PBFSFileStorage import PBFSFileStorage
from apiutils.HTTPResponses import *
from apiutils.DBClasses.JSONMemeDB import JSONMemeDB
from apiutils.MemeManagement.MemeLibrary import MemeLibrary
from apiutils.UploadSessionManager import UploadSessionManager
from apiutils.configs.ServerConfig import ServerConfig

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

# TODO: Fix this mess of initialization
JSONMemeDB.initSingleton(PBFSFileStorage(ServerConfig.PBFS_ACCESS_TOKEN, ServerConfig.PBFS_SERVER_IDENTIFIER))
MemeLibrary.initSingleton(JSONMemeDB.getSingleton(), testing=True)

memeLib = MemeLibrary.getSingleton()
memeLib.makeLibraryFromCSV(os.path.join(ServerConfig.PROJECT_ROOT, 'data', 'catalog.csv'))
memeLib.indexLibrary()


# @app.route('/myConsole', methods=['GET', 'POST'])
# def route_console():
#     return render_template('console.html', content=app.config['ALLOWED_EXTENSIONS'])


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

    matchedMemes = memeLib.findMemes(query)
    collated = [ {
        'name': meme.getName(),
        'url': meme.getURL() }
    for meme in matchedMemes]

    return make_json_response({ 'results' : collated})
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