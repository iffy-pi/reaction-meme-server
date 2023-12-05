import io
import mimetypes
import os
import json
import time


from flask import (Flask, flash, redirect, render_template, request, send_file,
                   session, url_for, Response)
from flask_cors import CORS 
from apiutils.HTTPResponses import *
from apiutils.MediaDB import MediaDB
from apiutils.FileServers.LocalDBFileServer import LocalDBFileServer
from apiutils.UploadSessionManager import UploadSessionManager
from apiutils.configs.config import ALLOWED_ACCESS_TOKENS
import uuid

# initialize app flask object
app = Flask(__name__)
CORS(app)

# TODO: Fix this mess of initialization
app.config['SECRET_KEY'] = "helloworld"

lfs = LocalDBFileServer()
mdb = MediaDB(lfs)
mdb.initDBToCatalog()
mdb.indexDB()

smInit = UploadSessionManager.getInstance()

# UTILITIES --------------------------------------------------------------------------------------------------------
@app.route('/myConsole', methods=['GET', 'POST'])
def route_console():
    return render_template('console.html', content=app.config['ALLOWED_EXTENSIONS'])


# # to download a file submitted to the server
# # you can use url_for('route_download_file', filename=<filename>) to get url for specific file
# @app.route('/uploads/<path:filepath>', methods=['GET', 'POST'])
# def route_download_file(filepath):
#     # Appending app path to upload folder path within app root folder
#     # Returning file from the pushbullet file server
#     pbfs_file_path = '/{}'.format(filepath)
#     file_content = pbfs.download_binary_from_path(pbfs_file_path)

#     if file_content is None:
#         return '{}\n{}'.format(pbfs_file_path, pbfs.get_file_index())

#     return send_file(
#         io.BytesIO(file_content),
#         download_name=filepath.split('/')[-1],
#         mimetype = mimetypes.MimeTypes().guess_type(filepath.split('/')[-1])[0],
#         as_attachment=True
#     )

@app.route('/memes/download/<int:memeID>', methods=['GET'])
def route_get_meme(memeID):
    memeID = str(memeID)
    if not mdb.hasItem(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    memeURL = mdb.getItemURL(memeID)
    return redirect(memeURL)

@app.route('/memes/search', methods=['GET'])
def route_meme_search():
    query = request.args.get("query")
    if query is None or query == "":
        return error_response(400, 'No query found, use "query" for the URL parameter')

    results = mdb.findItemIDsFor(query)
    collated = [ {
        'name': mdb.getItemName(itemId),
        'url': mdb.getItemURL(itemId) }
    for itemId in results]

    return make_json_response({ 'results' : collated})

def validAccess(req:request):
    accToken = req.headers.get('Access-Token')
    if accToken is None:
        return False
    if accToken not in ALLOWED_ACCESS_TOKENS:
        return False
    return True

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
    itemId = mdb.createNewItem(name=request.json['name'], tags=tags, fileExt=request.json['fileExt'])

    # respond with the item informaion and an upload URL
    sm = UploadSessionManager.getInstance()
    return make_json_response(
        {
            "id": itemId,
            "name": mdb.getItemName(itemId),
            "tags" : mdb.getItemTags(itemId),
            "fileExt": mdb.getItemFileExt(itemId),
            "uploadURL": url_for("upload_meme", itemId=itemId, _external=True),
            "Upload-Key": sm.newSession(itemId)
        }
    )

@app.route('/memes/upload/<int:itemId>', methods=['GET', 'POST'])
def upload_meme(itemId):
    if not validAccess(request):
        return error_response(400, 'Invalid Access Token')

    itemId = str(itemId)

    if not mdb.hasItem(itemId):
        return error_response(400, "Invalid item ID")

    sm = UploadSessionManager.getInstance()

    # check if the upload key included in the header matches
    uploadKey = request.headers.get('Upload-Key')
    if uploadKey is None or sm.getSession(itemId) is None or uploadKey != sm.getSession(itemId):
        return error_response(400, "Invalid upload session")

    # valid upload session get the image data
    mediaBinary = request.data

    # make the upload here
    cloudURL = mdb.uploadItemMedia(itemId, mediaBinary)

    # clear the upload session
    sm.clearSession(itemId)


    # TODO: Asynchronously save the db and reindex for future calls?
    mdb.saveDBChanges()
    mdb.indexDB()

    return make_json_response({'url': cloudURL})

# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Hello World'})

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)