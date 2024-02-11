# The Local Meme Storage Server
This is a server designed to store meme media on the local device. It was designed to mimic the behaviour of Cloudinary, our production solution for media storage. The server allows us to do testing and development without uploading garbage or consuming credits on Cloudinary.

## Running The Server
The server is a simple flask server which runs on port 5001. You can run the server by entering running `flask run --host=0.0.0.0 --port=5001` in this directory.

You can also run the server using the `local meme storage` run configuration in PyCharm.

## Using The Server
The server is used by the Reaction Meme Server by using the LocalMediaStorage class, which is designed to make calls the local storage server. The function makeLocalStorage defined in utils/LocalStorageUtils creates the LocalMediaStorage object with its appropriate parameters.

When the server is in development mode or testing mode, the local storage meme server will be used unless there are specific overrides.

## How The Server Works
The server stores the meme media in the storage/memes directory (which has been configured to be ignored by Git).

When a new media request is received by the server, it:
1. Generates a new media ID
2. Saves the media file in the memes directory as `meme_<media ID>.<file extension>`

Media ID generation is managed by storage/config.json, which stores the nextID to be used by the server. For each new media request, the server gets the next ID and increments the ID stored in the JSON by 1 for the new ID.

## Automatic Cloud To Local Translation
As mentioned above, the local meme storage server is used by default during testing. Therefore, to accomodate cases where new memes were added to the library on Cloudinary, the automatic translation of cloud memes to local memes was designed.

### How translations are stored
Translations are managed by storage/cloudMap.json, which is a JSON dictionary that maps each media ID on the cloud to the media ID on the local meme storage server:

```json
{
  "memes/felvt9yr45ad5ktyevg2": {
        "cloudID": "memes/felvt9yr45ad5ktyevg2",
        "cloudURL": "http://res.cloudinary.com/du6q7wdat/video/upload/v1/memes/felvt9yr45ad5ktyevg2",
        "localID": "446",
        "localURL": "http://127.0.0.1:5001/local/meme/446"
    }
}
```

### When/How Translations Happen
The translation runs whenever MemeContainer.getMediaID or MemeContainer.getMediaURL is run (except if the autoConvertToLocal parameter for the methods is set to false).

Within the call to these methods, the function cloudMemeNeedsToBeConvertedToLocal (in LocalStorageUtils) is called to determine if the given media ID and media URL needs to be converted into the media ID and media URL of the same meme on the local storage server. This function returns true only if:
- The server is NOT in production mode (unless ignoreEnv is true)
- The server's configured meme storage is local meme storage
- The media URL is not a local one
  - It does not include the local host or the remote host IP address

If the function returns true, the function getLocalVersionForCloudMeme is called to complete the translation:
- The function checks if the cloud ID already exists in cloudMap.json, if so it returns the local media ID and local media URL
- If not, the function downloads the meme using the cloud URL, and then uploads it to the local meme storage server. It then saves the local media ID and media URL into cloudMap.json, and returns it.