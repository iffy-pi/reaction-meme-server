# Technical README
This is the README that covers the technical information about the project.

# Configuration Notes
## Deployment Notes
The current setup of the project has the following deployment configured:
- The server is hosted on Vercel under my account as the reaction-meme-server project
- The PushBullet account used for the file server is hosted with my bot email address.
- Cloudinary hosts the meme media files, tied to my GitHub email

## Config Variables
Access tokens, the development environment and other environment constants are managed with the ServerConfig class (apiutils/ServerConfig).

This class stores relevant information in its static class members, which we can call "config variables". These class members are accessed in other areas of the API to determine the behaviour. You can initialize the config variables by:
- Setting the correct environment variables (`ServerConfig.setConfigFromEnv`)
- Passing a JSON file with the correct key-value pairs (`ServerConfig.setConfigFromJSON`)

The following keys (or environment variable names) are checked for when initializing the config variables
- `RMSVR_PROJECT_ENVIRONMENT`
  - Required
  - The running environment of the project
  - Can be either `development` or `production`
- `RMSVR_ALLOWED_ACCESS_TOKENS`
  - Required
  - The access tokens which are allowed to edit/add new memes to the server
  - Are `;` separated
- `RMSVR_CLOUDINARY_CLOUD_NAME`
  - Required, if using Cloudinary
  - The name of the server on your cloudinary account
- `RMSVR_CLOUDINARY_API_KEY`
  - Required, if using Cloudinary
  - The API key of the cloudinary server (Cloudinary Console > Settings > Access Keys)
- `RMSVR_CLOUDINARY_API_SECRET`
  - Required, if using Cloudinary
  - The API secret of the cloudinary server (Cloudinary Console > Settings > Access Keys)
- `RMSVR_MEME_DB`
  - Optional
  - What type of DB will be used by the library
  - Can be `json` (default)
- `RMSVR_MEME_STORAGE`
  - Optional
  - What type of meme storage is used by the library
  - Can be:
    - `cloudinary`: default, for Cloudinary hosting
    - `local` : For local meme storage server
- `RMSVR_JSON_DB_FILE_STORAGE`
  - Optional
  - What type of file storage is used by the JSON Meme DB
  - Can be:
    - `pbfs`: default, uses the PushBullet File Server
    - `local`: Saves it to local repository file
- `RMSVR_PBFS_ACCESS_TOKEN`
  - Required, if using PushBullet
  - The access token of the PushBullet account
- `RMSVR_PBFS_SERVER_IDENTIFIER`
  - Required, if using PushBullet
  - The server identifier of the

## Runtime Environments
### Runtime Overrides
The config variables determine the components used at runtime, however there can be overrides done to config variables using some special environment variables:

- `JSON_ENV`
  - If present, it will be treated as a file path to the JSON file which will be used to initialize the config variables
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
- `INIT_LIB_FROM_CATALOG_OVERRIDE`
  - If the env var exists, the library will be initialized from data/catalog.csv
  - If it does not exist, the library will be initialized from the connected meme DB

### Available Runtime Configurations
There are different runtime configurations that have been made in PyCharm, which use the environment variables:
- `api (prod)`
  - Mirrors server running in production environment:
    - File Storage: PBFS (ReactionMemeServer PB device)
    - Meme DB: JSON Meme DB
    - Meme Storage: Cloudinary
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_ENV = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\prodenv.json`


- `api (dev)`
  - Server in development
    - File Storage: PBFS (ReactionMemeServer-DevEnv PB device)
    - Meme DB: JSON Meme DB
    - Meme Storage: Local
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_ENV = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv.json`

- `api (db=json, ms=local, fs=local)`
  - Server in development
    - File Storage: Local (RepoLocalFileStorage)
    - Meme DB: JSON Meme DB
    - Meme Storage: Local
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_ENV = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\devenv.json`
    - `OVERRIDE_RMSVR_JSON_DB_FILE_STORAGE = local`
    - `OVERRIDE_RMSVR_MEME_DB = json`
    - `OVERRIDE_RMSVR_MEME_STORAGE = local`

- `api (db=json, ms=cloud, fs=local)`
  - Server in development
    - File Storage: Local (RepoLocalFileStorage)
    - Meme DB: JSON Meme DB
    - Meme Storage: Cloudinary
    - Library Source: Loaded From DB
  - Env Vars
    - `JSON_ENV = C:\Users\omnic\local\GitRepos\reaction-meme-server\devenv\devenv.json`
    - `OVERRIDE_RMSVR_JSON_DB_FILE_STORAGE = local`
    - `OVERRIDE_RMSVR_MEME_DB = json`
    - `OVERRIDE_RMSVR_MEME_STORAGE = cloudinary`

# Software Details
***This section is still in development, added for posterity***
## `MemeLibrary`
The main class being used for meme management is the MemeLibrary class (`apiutils/MemeManagement/MemeLibrary.py). This class is initialized and handles searching for memes, adding new memes to the library and so on.

The MemeLibrary class is more like a coordinator which uses other classes to complete the required tasks, the classes involved are:
- MemeLibraryItem
- MemeUploaderInterface : The uploader argument in MemeLibrary constructor
- MemeDBInterface : The db argument in MemeLibrary constructor

## `MemeLibraryItem`
Like a book from the library, a MemeLibraryItem is an object which contains all relevant information about a meme, this includes its name, file extension, tags and URL.

The class provides getter and setter methods for a MemeLibraryItem, but it is important to note that MemeLibraryItem instances **are not linked to the library**. That is, changes to a MemeLibraryItem do not affect the actual library or underlying database. The class is primarily used as a data container for memes.

## `MemeUploaderInterface`
This is an "interface" used by MemeLibrary to handle uploading the binary content of meme files to the hosting service in use.

Classes which implement the MemeUploaderInterface can be passed to MemeLibrary as the uploader. Using an interface allows different hosting solutions to be implemented and used in MemeLibrary without having to change any code within the class (a plug-and-play).

There are two classes which implement the MemeUploader interface:
- CloudinaryUploader (`apiutils/MemeUploaderClasses/CloudinaryUploader`) handles uploadig to cloudinary.
- LocalStorageUploader (`apiutils/MemeUploaderClasses/LocalStorageUploader`) handles uploading as saving onto your local device. It's specifically implemented for a testing environment.

### Local media hosting with `LocalStorageUploader`
LocalStorageUploader is designed to work with the local meme storage server configuration which allows me to mimic cloud hosting but instead saving locally. Read more in `localMemeStorage\README.md`

## `MemeDBInterface`
This interface provides the similar plug-and-play solution but instead for the database used within MemeLibrary. The meme database stores the related information for each meme, which includes the meme's:
- ID: The unique ID in the database for the meme entry
- Name: A descriptive name for the meme
- Tags: The set of tags associated with the eme
- Cloud ID: The ID used for the meme in the cloud hosting service
- Cloud URL: The URL from which the meme can be downloaded

Any implementing classes for the MemeDBInterface will have these fields to some degree, the specific implementation will vary. For this there is only one implementing class available:
- JSONMemeDB : A database implementation just using a JSON file