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

# initialize app flask object
app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "helloworld"

lfs = LocalDBFileServer()
mdb = MediaDB(lfs)
mdb.initDBToCatalog()
mdb.indexDB()

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

@app.route('/memes/<int:memeID>', methods=['GET'])
def route_get_meme(memeID):
    memeID = str(memeID)
    if not mdb.hasItem(memeID):
        return error_response(400, message=f"ID {memeID} does not exist in database")

    memeURL = mdb.getPropertyForItemID(memeID, MediaDB.DBFields.ItemFields.CloudURL)
    return redirect(memeURL)

# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Hello World'})

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)