# The local storage server
The server allows me to mimic the behaviour of cloud hosting provided by Cloudinary, meaning that testing can be performed without uploading garbage or reducing available credits on Cloudinary.

The server works in two ways:
- Running the server by running `app.py`
- Plugging in the server to MemeLibrary using `makeLocalStorageUploader` in `utils/storageServerUtils.py`
  - This is the uploader passed to MemeLibrary, and is designed to work the local system

The server is designed to run on your local system on port 5001, since the main API will be on port 5000.

## Running the server
In this directory, use `flask run --host=0.0.0.0 --port=5001`. PyCharm has already been configured with a local meme storage run configuration, use tha to run the server


## Other notes
- The .gitignore has been configured to ignore the meme directory, except the README file