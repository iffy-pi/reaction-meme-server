# import threading

from flask import (Flask, request, send_from_directory, render_template, url_for)
from flask_cors import CORS

from api.endpoints import *
from api.functions import initAndIndexMemeLibrary, validAccess, serverErrorResponse, checkReqJSONParameters, \
    checkDictionaryParams
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
def route_download_meme(memeID: int):
    try:
        return downloadMeme(memeID, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/info/<int:memeID>', methods=['GET'])
def route_info_meme(memeID: int):
    try:
        return getMemeInfo(memeID, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/edit/<int:memeID>', methods=['POST'])
def route_edit_meme(memeID: int):
    try:
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')

        paramInfo = [
            ('name', False, str),
            ('tags', False, list)
        ]

        good, msg = checkReqJSONParameters(request, paramInfo)
        if not good:
            return error_response(400, msg)

        name = request.json.get('name')
        tags = request.json.get('tags')

        return editMeme(memeID, name, tags, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/browse', methods=['GET'])
def route_meme_browse():
    try:
        paramInfo = [
            ('page', True, str),
            ('per_page', True, str)
        ]

        good, msg = checkDictionaryParams(request.args, paramInfo)
        if not good:
            return error_response(400, msg)

        try:
            itemsPerPage = int(request.args['per_page'])
            pageNo = int(request.args['page'])
        except ValueError:
            return error_response(400, '"per_page" and/or "page" parameter is a non-integer value')


        return browseMemes(itemsPerPage, pageNo, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/search', methods=['GET'])
def route_meme_search():
    try:
        paramInfo = [
            ('query', True, str),
            ('page', False, str),
            ('per_page', False, str),
            ('media_type', False, str)
        ]

        good, msg = checkDictionaryParams(request.args, paramInfo)
        if not good:
            return error_response(400, msg)

        query = request.args.get("query")
        pageNo = request.args.get("page")
        itemsPerPage = request.args.get("per_page")
        mediaTypeStr = request.args.get("media_type")

        if itemsPerPage is not None:
            try:
                itemsPerPage = int(itemsPerPage)
            except ValueError:
                return error_response(400, '"per_page" parameter is a non-integer value')

        if pageNo is not None:
            try:
                pageNo = int(pageNo)
            except ValueError:
                return error_response(400, '"page" parameter is a non-integer value')

        return searchMemes(query, itemsPerPage, pageNo, mediaTypeStr, memeLib)
    except Exception as e:
        return serverErrorResponse(e)


@app.route('/add', methods=['POST'])
def route_add_new_meme():
    try:
        if not validAccess(request):
            return error_response(400, 'Invalid Access Token')

        paramInfo = [
            ('name', True, str),
            ('tags', True, list),
            ('fileExt', True, str),
            ('mediaID', True, str),
            ('mediaURL', True, str,)
        ]

        good, msg = checkReqJSONParameters(request, paramInfo)
        if not good:
            return error_response(400, msg)

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

        if 'fileExt' not in request.form:
            return error_response(400, "Missing parameter: 'fileExt'")

        if 'file' not in request.files:
            return error_response(400, "No file property included in upload request")

        file = request.files['file']
        fileExt = request.form['fileExt']

        return uploadMeme(fileExt, file, memeLib)

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