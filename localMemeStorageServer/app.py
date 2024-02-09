import os
import subprocess

from flask import (Flask, send_from_directory, request, url_for)
from flask_cors import CORS

from apiutils.configs.ServerConfig import ServerConfig
from localMemeStorageServer.utils.LocalStorageUtils import getMemeDir, makeLocalMemeStorage, getMemeFileName, \
    getConfigJSONPath, getMemeFileForID
from apiutils.HTTPResponses import *

ServerConfig.setConfigFromJSON(ServerConfig.path('devenv/config_jsons/devenv.json'))

# initialize app flask object
app = Flask(__name__)
CORS(app)

@app.route('/local/meme/<int:mediaID>')
def route_get_media(mediaID: int):
    memeName = getMemeFileName(mediaID)
    if memeName is None:
        return error_response(400, f"Meme {mediaID} not found")
    return send_from_directory(getMemeDir(), memeName)



@app.route('/local/upload', methods=['POST'])
def route_upload_media():
    fileExt = request.args.get('fileExt')

    if fileExt is None:
        return error_response(400, 'File extension is not included')

    mediaBinary = request.data
    memeDir = getMemeDir()
    configFile = getConfigJSONPath()

    # get the next id
    with open(configFile, "r") as file:
        config = json.load(file)

    mediaID = int(config["nextID"])

    # save the binary to the location
    filename = f"meme_{mediaID}.{fileExt}"

    with open(os.path.join(memeDir, filename), "wb") as file:
        file.write(mediaBinary)

    # update nextId
    config["nextID"] = mediaID + 1

    with open(configFile, "w") as file:
        json.dump(config, file, indent=4)

    # return the ID and url
    return make_json_response({
        'mediaID': mediaID,
        'mediaURL': url_for("route_get_media", mediaID=mediaID, _external=True),
    })

@app.route('/local/thumbnail/<int:mediaID>')
def route_make_thumbnail(mediaID: int):
    memeFile = getMemeFileForID(mediaID)

    if memeFile is None:
        return error_response(400, f'Meme file not found for id {mediaID}')

    imgOut = ServerConfig.path('localMemeStorageServer', 'temp.jpeg')

    child = subprocess.Popen(
        ['ffmpeg.exe', '-i', memeFile, '-ss', '00:00:00.000', '-vframes', '1', imgOut, '-y', '-loglevel', '0'],
        stdout=subprocess.PIPE)

    child.wait()

    rc = child.returncode
    if rc != 0:
        return error_response(500, 'An error occurred converting the video with ffmpeg')

    # read the bytes
    with open(imgOut, 'rb') as file:
        bts = file.read()

    # delete the temp image
    os.remove(imgOut)

    return bts


# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Hello World'})


# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)