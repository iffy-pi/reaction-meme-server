from flask import (Flask,  send_from_directory, request)
from flask_cors import CORS
from localMemeStorageServer.utils.LocalStorageUtils import getMemeDir, makeLocalMemeStorage, getMemeFileName
from apiutils.HTTPResponses import *

# initialize app flask object
app = Flask(__name__)
CORS(app)

@app.route('/local/meme/<id>')
def get_meme(id):
    memeName = getMemeFileName(id)
    if memeName is None:
        return error_response(400, f"Meme {id} not found")
    return send_from_directory(getMemeDir(), memeName)


# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Hello World'})

# TODO local uploading
@app.route('/local/meme/upload', methods=['GET', 'POST'])
def upload_meme():
    # valid upload session get the image  data
    mediaBinary = request.data
    upl = makeLocalMemeStorage()
    cloudID, cloudURL = upl.uploadMedia(mediaBinary, 'mp4')

    return make_json_response({'url': cloudURL})

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)