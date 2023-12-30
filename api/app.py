# import threading

from flask import (Flask, request, send_from_directory)
from flask_cors import CORS

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

# Initialize our library
memeLib = initAndIndexMemeLibrary()


@app.route('/download/<int:memeID>', methods=['GET'])
def route_download_meme(memeID):
    try:
        downloadMeme(memeID, memeLib)
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
        return editMeme(memeID, request.json.get("name"), request.json.get("tags"), memeLib)
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
        return addNewMeme(request.json.get("name"),
                          request.json.get("tags"),
                          request.json.get("fileExt"),
                          request.json.get("cloudID"),
                          request.json.get("cloudURL"),
                          memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/upload-request', methods=['POST'])
def route_upload_request():
    try:
        return uploadMemeRequest(request.json.get("fileExt"))
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/upload/<sessionKey>', methods=['POST'])
def route_upload_meme(sessionKey):
    try:
        return uploadMeme(sessionKey, request.data, memeLib)
    except Exception as e:
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
        return serverErrorResponse(e)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(ServerConfig.PROJECT_ROOT, 'favicon.ico')


# for the root of the website, we would just pass in "/" for the url
@app.route('/')
def index():
    return make_json_response({ 'message': 'Welcome To Meme Server, checkout the API usage: https://github.com/iffy-pi/reaction-meme-server?tab=readme-ov-file#api-documentation'})

# TODO: Implement Apple Shortcuts client API :D
# TODO: Build the React client frontend :(((

# running the code
if __name__ == '__main__':
    # debug is true to show errors on the webpage
    app.run(debug=True)