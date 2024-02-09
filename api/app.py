# import threading

from flask import (Flask, request, send_from_directory, render_template, flash)
from flask_cors import CORS
from werkzeug.datastructures import ImmutableMultiDict, FileStorage

from api.endpoints import *
from api.functions import initAndIndexMemeLibrary, validAccess, serverErrorResponse
from apiutils.HTTPResponses import *
from apiutils.configs.ServerConfig import ServerConfig

# Initialize our server config
ServerConfig.initConfig()
print('')
ServerConfig.printConfig()

# initialize app flask object
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = ServerConfig.PBFS_ACCESS_TOKEN

# Initialize our library
memeLib = initAndIndexMemeLibrary()


@app.route('/download/<int:memeID>', methods=['GET'])
def route_download_meme(memeID):
    try:
        return downloadMeme(memeID, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/info/<int:memeID>', methods=['GET'])
def route_info_meme(memeID):
    try:
        return getMemeInfo(memeID, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/edit/<int:memeID>', methods=['POST'])
def route_edit_meme(memeID):
    try:
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')
        name = None
        tags = None
        if request.is_json:
            name = request.json.get("name")
            tags = request.json.get("tags")
        return editMeme(memeID, name, tags, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/browse', methods=['GET'])
def route_meme_browse():
    try:
        return browseMemes(request.args.get("per_page"), request.args.get("page"), memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/search', methods=['GET'])
def route_meme_search():
    try:
        return searchMemes(request.args.get("query"), request.args.get("per_page"), request.args.get("page"), request.args.get("media_type"), memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/add', methods=['POST'])
def route_add_new_meme():
    try:
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')
        return addNewMeme(request.json.get("name"),
                          request.json.get("tags"),
                          request.json.get("fileExt"),
                          request.json.get("mediaID"),
                          request.json.get("mediaURL"),
                          memeLib)
    except Exception as e:
        return serverErrorResponse(e)

@app.route('/upload', methods=['POST'])
def route_upload_meme():
    try:
        if request.method != 'POST':
            return error_response(400, 'Invalid Method')

        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')

        return uploadMemeNew(request.form, request.files, memeLib)

    except Exception as e:
        return serverErrorResponse(e)


@app.route('/admin/reset')
def reset_meme_lib():
    if not validAccess(request):
        return error_response(400, 'Invalid Access Token')

    global memeLib
    memeLib = initAndIndexMemeLibrary()
    return make_json_response({'message': 'Library Reset'})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(ServerConfig.PROJECT_ROOT, 'favicon.ico')


@app.route('/media/<mediaName>')
def getMedia(mediaName):
    mediaName = str(mediaName)
    mediaDir = ServerConfig.path('media')

    if not os.path.exists(os.path.join(mediaDir, mediaName)):
        return error_response(400, "Unknown media!")

    return send_from_directory(mediaDir, mediaName)

# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    hostURL = url_for("index", _external=True)
    return render_template('index.html', publicURL=hostURL)

# TODO: Implement Apple Shortcuts client API :D
# TODO: Build the React client frontend :(((

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)