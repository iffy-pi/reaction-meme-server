# Technical README
This is the README that covers the technical information about the project.

# Configuration Notes
## Deployment Notes
The current setup of the project has the following deployment configured:
- The server is hosted on Vercel as the reaction-meme-server project
- The PushBullet account used for the file server is hosted with my bot email address.
- Cloudinary hosts the meme media files.

## Config Variables
Access tokens, the development environment and other environment constants are managed with the ServerConfig class (apiutils/configs/ServerConfig.py).

This class stores relevant information in its static class members, which we can call "config variables". These class members are accessed in other areas of the API to determine the behaviour. You can initialize the config variables by:
- Setting the correct environment variables (`ServerConfig.setConfigFromEnv`)
- Passing a JSON file with the correct key-value pairs (`ServerConfig.setConfigFromJSON`)

Read the class source code for more information.

## Runtime Environments
### Runtime Overrides
The ServerConfig class provides the option to override specific config variables, even after initializing the config from an environment or JSON file. The overrides are done through the environment variables found at runtime.

These overrides allow you to make different run configurations for the server without having to create multiple JSON config files. Instead, you have the base configuration file e.g. (devenv.json), which contains the base configuration and non-changing config variables (e.g. access tokens, project environment) and use the overrides to have specific types of the configuration (e.g. one configuration uses the local meme storage, the other configuration uses Cloudinary).

The provided overrides are listed below. Use these as environment variable names for the override to work:
- `JSON_CONFIG`
  - If present, it's value  will be treated as a file path to the JSON file which will be used to initialize the config variables
- `OVERRIDE_RMSVR_MEME_DB`
  - Overrides the database used by the meme library for the memes
  - Options:
    - See options for `RMSVR_MEME_DB` config variable
- `OVERRIDE_RMSVR_JSON_DB_FILE_STORAGE`
  - Overrides the file storage used by the JSON Database
  - Options:
    - See options for `RMSVR_JSON_DB_FILE_STORAGE` config variable
- `OVERRIDE_RMSVR_MEME_STORAGE`
  - Overrides the meme storage (where memes are uploaded to)
  - Options:
    - See options for `RMSVR_MEME_STORAGE` config variable

### Server Run Configurations
There are different runtime configurations that have been made in PyCharm, which use the environment variables:
- `api (prod)`
  - Mirrors server running in production environment:
    - Meme DB: JSON Meme DB
    - File Storage: PBFS (ReactionMemeServer-Prod PB device)
    - Meme Storage: Cloudinary
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_CONFIG = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\config_jsons\prodenv.json`

- `api (dev)`
  - Server in development
    - Meme DB: JSON Meme DB
    - File Storage: PBFS (ReactionMemeServer-DevEnv PB device)
    - Meme Storage: Local
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_CONFIG = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\config_jsons\devenv.json`

- `api (test)`
  - Used when running server tests
  - Server in testing mode
    - Meme DB: JSON Meme DB
    - File Storage: Local (RepoLocalFileStorage)
    - Meme Storage: Local
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_CONFIG = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\config_jsons\testenv.json`

- `api (db=json, ms=local, fs=local)`
  - Server in development
    - Meme DB: JSON Meme DB
    - File Storage: Local (RepoLocalFileStorage)
    - Meme Storage: Local
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_CONFIG = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\devenv.json`
    - `OVERRIDE_RMSVR_JSON_DB_FILE_STORAGE = local`
    - `OVERRIDE_RMSVR_MEME_DB = json`
    - `OVERRIDE_RMSVR_MEME_STORAGE = local`

- `api (db=json, ms=cloud, fs=local)`
  - Server in development
    - Meme DB: JSON Meme DB
    - File Storage: Local (RepoLocalFileStorage)
    - Meme Storage: Cloudinary
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_CONFIG = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\devenv.json`
    - `OVERRIDE_RMSVR_JSON_DB_FILE_STORAGE = local`
    - `OVERRIDE_RMSVR_MEME_DB = json`
    - `OVERRIDE_RMSVR_MEME_STORAGE = cloudinary`

### Other Run Configurations
- `local meme storage`
  - Used to run the local meme storage server
- `API Tests`
  - Runs the suite of tests designed for the reaction meme server

# Server Testing
The server is tested using Python unit tests on each of the endpoints defined in the documentation. These unit tests (defined in server_void/testing/APITests.py) were designed to ensure that the server performed correctly when parsing and handling requests.

To run tests:
1. Run the `local meme storage` configuration to start the local meme storage server
2. Run the `api (test)` configuration to start the server in testing mode
  - This switches the server to write to data/testing_db.json, which is inspected while running tests
3. Run the actual tests with the `API Tests` configuration

# Software Overview
***This section is still in development, added for posterity***

This is intended to give an overview of how the server works, such that ad developer can familiarize themselves with the code on a later date. It will begin at the high level function of the server, and expand on the relevant files and concepts used in the system.

A diagram of the overview of the server function is provided below:

TODO: Add diagram

## The API
The server performs functions through the Flask-powered REST API. The Flask server (api/app.py) defines the functions for each endpoint discussed in the [API documentation](../README.md).

When the server is started it:
- Initializes the ServerConfig using environment variables, which will be available in the Vercel runtime.
- initializes a MemeLibrary object as a global variable, which is shared by all the functions used in the server.
  - MemeLibrary initialization involves configuring the meme database and meme storage for the library, as well as loading the library into memory

The general design of the server routes is as follows. For a given API call, the server:
1. Checks and sanitizes the client request. The server will return a HTTP 400 status code if the client request data is not syntactically valid.
2. If the client request data is correct, it is passed as a parameter to the appropriate endpoint function (found in api/endpoints.py) for that API endpoint. The endpoint function is also passed the global MemeLibrary object for its operation.
  - The endpoint function may return a HTTP 400 status code if the client request cannot be processed due to semantic invalidity (e.g. the request meme ID does not exist)
  - Otherwise, it creates the server response according to the API documentation and returns it to the calling route, which is then what the server responds with to the client.

## MemeLibrary
### Overview
The MemeLibrary class (apiutils/MemeManagement/MemeLibrary.py) implements the code to manage memes for the Reaction Meme Server. The class provides methods for many operations, including:
- Finding memes in the library based on a query
- Adding new memes to the library
- Editing the properties of memes already in the library
- Uploading the media (image/video file) associated with a meme

Therefore, an instance of the MemeLibrary is used by the servers endpoint functions. The server acts as a translator between the client and the MemeLibrary, parsing client requests, calling the appropriate MemeLibrary method and then packaging method output for the client.

### Structure
The MemeLibrary works by co-ordinating operations between different aspects of the library:
- The meme database
  - The meme database stores all the information about a meme, such as its name, tags etc.
  - The meme database is controlled through an object that implements the MemeDB interface. This object is passed into the MemeLibrary as one of its constructor arguments.
- The meme media storage
  - This handles the uploading and downloading of meme media, and the generation of delivery URLs for said meme media
  - It is controlled through an object that implements the MemeStorage interface. This object is passed into the MemeLibrary as one of its constructor arguments.
- The meme searcher
  - This handles the indexing and searching of memes in the library.
  - An instance of the MemeLibrarySearcher class is created and stored within a MemeLibrary object.

## MemeContainer
The MemeContainer class (apiutils/MemeManagement/MemeContainer.py) is used within MemeLibrary and other areas of the server as the data container for all information about a given meme. The class stores the meme information as its properties, and provides methods to get/set those properties for a meme. These properties are:

| Name        | Data Type     | Description                                                                                                                              |
|-------------|---------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `id`        | Integer       | The ID of the meme in the meme database                                                                                                  |
| `name`      | String        | The colloqial name of the meme e.g "girl happy at target"                                                                                |
| `tags`      | List          | The list of tags associated with the meme, used to help find the meme when searching for it                                              |
| `fileExt`   | String        | The file extension of the media file associated with the meme                                                                            |
| `mediaType` | MemeMediaType | The media type (either image or video) of the meme media. The media type is stored with the meme as it is helpful when performing search |
| `mediaID`   | String        | The ID of the meme's media in the media storage                                                                                          |
| `mediaURL`  | String        | The delivery URL of the meme media. That is, the URL which can be used to download the meme media                                        |
| `thumbnail` | String        | A base64-encoded 100x100 JPEG thumbnail of the meme media. Helpful for quick previews of a meme                                          |

The MemeContainer is only used as a data container to pass information about memes between different functions. It is often the output of many of MemeLibrary's methods, and is used as a parameter in the MemeDB interface. **It is not implicitly connected to the meme database**.

### Automatic Conversions of Media Properties to Local Meme Storage
When getting the mediaID and mediaURL through the MemeContainer, if the specific conditions have been set, the getter method will automatically return the mediaID and mediaURL of the meme in the Local Meme Storage rather than its actual media source.

The original mediaID and mediaURL are still stored within the MemeContainer, the 'conversion' is only done when requesting data through the getter method. This automatic conversion can be directly disabled by setting the `autoConvertToLocal` optional parameter of the getter method to false.

The automatic conversion was introduced to simplify testing and development, since it will be enabled if the server is running in the development environment. You can read more about this in [Local Meme Storage](../localMemeStorageServer/README.md).

## The Meme Database (MemeDBInterface)
The meme database stores the information about each meme in the library. It is handled through the MemeDB interface (apiutils/MemeManagement/MemeDBInterface.py), which defines the set of methods a class must implement to be used as a database. This implementation allows database solutions to be 'plug-and-play', if a different database solution is available, then we simply need to design its class which implements the MemeDB interface.

The interface has methods for:
- Initializing a new database
- Loading the database into memory
- Retrieving a meme or sets of memes from the database
- Creating new memes in the database
- Updating memes in the database

### JSONMemeDB
The JSONMemeDB class (apiutils/MemeDB/JSONMemeDB.py) implements the meme database as a simple JSON file. The file format is shown below:

```json
{
    "nextID": 423,
    "items": {
        "0": {
          "id": 0,
          "name": "full time professional clown",
          "mediaType": "video",
          "fileExt": "mp4",
          "tags": [
            "clown",
            "clownsville",
            "full time clown",
            "professional clown"
          ],
          "mediaID": "memes/m2bob7x7euz7yqyhc24g",
          "mediaURL": "http://res.cloudinary.com/du6q7wdat/video/upload/v1/memes/m2bob7x7euz7yqyhc24g",
          "thumbnail": "..."
        }
    }
}
```

- The `nextID` field stores the ID that will be used when a new meme is created
- The `items` field is a dictionary that maps each meme ID to its dictionary of information

Since the database is a JSON file, it will have to be saved and stored in order to be used. For this, the JSONMemeDB follows a similar 'plug-and-play' approach like MemeLibrary, where it defines the JSONDBFileStorageInterface (apiutils/FileStorage/JSONDBFileStorageInterface.py) to be implemented by relevant classes. There are two available implementations:
- LocalFileStorage (apiutils/FileStorage/LocalFileStorage.py)
  - JSON database is saved to data/db.json (saved to data/testing_db.json when server is in testing mode)
  - This is used for development and testing purposes
- PBFSFileStorage (apiutils/FileStorage/PBFSFileStorage.py)
  - JSON database is saved to PushBullet File Server (file server is initialized based on the PushBullet access token and server identifier in the server config).
  - This is the implementation used in production
  - The PushBullet devices available:
    - ReactionMemeServer-Prod
    - ReactionMemeServer-Test
    - ReactionMemeServer-DevEnv

*Editor's Note: This implementation of saving the JSON file is **VERY JANKY**, I am well aware. But as of right now, its the only easy way I know to save the JSON file.*

### Database Backups
There are two backup procedures in place for the database content:
- PushBullet Backups
  - Normally, the PBFS (PushBullet FIle Server) is configured to delete the previous version of a file when a new one is uploaded. This functionality was disabled, meaning that previous versions of the database will remain available on PushBullet.
- Backup To My Computer
  - The server-void/backups/back_up_json_db.py is a script which takes the current version of the JSON DB (on ReactionMemeServer-Prod) and saves it into the configured backup location: C:\Users\omnic\OneDrive\Computer Collection\Reaction Meme Server\backups\database
  - The script has been configured to run daily in the background using Windows Task Scheduler.
  - Read more in its [README](../server_void/backups/README.md).
 

## The Meme Media Storage (MemeStorageInterface)
The meme media storage stores the actual image and video files associated with each meme. Just like the meme database, there is the MemeStorageInterface class (apiutils/MemeManagement/MemeStorageInterface.py) which a class must implement to be a valid media storage class which can be passed to MemeLibrary.

The interface specifies methods that:
- Upload a given set of bytes for a meme's media, returning the media ID and delivery URL for that given meme. This is the mediaID and mediaURL information stored with the meme.
- Returns the bytes associated of a media file when given a media ID.
- Generate a thumbnail image for video media
  - This is used by MemeLibrary when generating the base64 encoded thumbnail

There are two implementations available for the MemeStorage:
- Cloudinary (apiutils/MemeStorage/CloudinaryMemeStorage)
  - Meme media is uploaded to the Cloudinary server using the credentials in the Server Config
  - This is the implementation used in production
- Local Storage (apiutils/MemeStorage/LocalMemeStorage)
  - This stores the meme media locally by making calls to the [Local Meme Storage Server](../localMemeStorageServer/README.md).
  - This is used in testing and development.

The choice of meme storage used when the server is running is based on the Server Config. The function getServerMemeStorage in apitutils/configs/ServerComponents parses the config variables and returns the appropriate meme storage object.

In the default developer and testing mode (i.e. the run configurations `api (dev)` and `api test`) the server will use the local meme storage.


## The Meme Searcher (MemeLibrarySearcher)
The MemeLibrarySearcher class (apiutils/MemeManagement/MemeLibrarySearcher.py) is used to index and search memes in the library. The class internally uses the [Whoosh Library](https://whoosh.readthedocs.io/en/latest/index.html) for these functions.

The searcher class provides methods to:
- Index A Meme: Add a meme to the library index so that it can be searched for
- Search For A Meme: Searches the index based on the given query and filters

### Indexing Memes
Memes are indexed following a Schema, which defines the information that is used when indexing the meme. This information includes:
- The meme's name, which is used when searching
- The meme's tags, which is used when searching
- The meme's media type, used to filter search results
- The meme's ID, stored and not used in search
- The meme's URL, stored and not used in search

All memes must be indexed for them to be searchable. The searcher provides methods to index one meme or a group of memes, and they are called by the server on startup through MemeLibrary.

### Searching For Memes
A search begins with a string query, which is parsed in an or-group strategy: the query "happy girl at target" will search for matches to "happy", "girl", "at", "target" and any combinations of them. This search strategy was chosen since we often remember only a specific word or phrase in the meme. 

This is also applied to the meme names, e.g. the meme name "happy dog evil" will be searchable as "happy", "dog", or "evil". Tags are similar, any combination of the tags will work but each tag is not space-separated searchable e.g. the tags `["happy dog","evil"]` will break down to "happy dog" and "evil" instead of "happy", "dog" and "evil".    

The search process also supports filtering, where a media type can be excluded from search or the search can be limited to only a specific media type.

The search results are returned as elements of the MemeHit class, a class similar in function to MemeContainer for the search results.
