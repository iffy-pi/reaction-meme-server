# reaction-meme-server
This is a Flask server hosted on Vercel designed to manage my reaction meme library. It provides HTTP API end points to download, browse, search, edit and add memes to the reaction meme library.

It is hosted on Vercel: https://reaction-meme-server.vercel.app/.

# API Documentation
## General Response Information
For each API endpoint, a successful response will have a `success` field which is set to true, and the data of the response will be in the `payload` field.


Erroneous responses (client and server errors) will have an `error` field set to true, and will always include an `error_message` field, which describes the cause of the error.

## Privileged Endpoints and Access Tokens
An endpoint with `(privileged)` tag is a privileged endpoint. Requests to privileged endpoints must be authenticated with an access token, included in the request header.

```python
{
    'Access-Token': '....' # Access Token Here
}
```

To get an access token, please contact the owner of the server.

## Available Endpoints
### Download Meme
This endpoint allows you to download memes from the server. A call to this endpoint will redirect to a delivery URL for the meme media bytes.

#### Call
```
GET https://reaction-meme-server.vercel.app/download/<memeID>
```
Where `<memeID>` is the ID of the meme to download.

#### Response
A redirect to the delivery URL of the meme media, which will then automatically download the meme.

#### Example
```python
import requests
resp = requests.get('https://reaction-meme-server.vercel.app/download/2')
with open('meme.jpg', 'wb') as file:
    file.write(resp.content)
```


### Get Meme Information
This returns stored information for a given meme in the library.

#### Call
```
GET https://reaction-meme-server.vercel.app/info/<memeID>
```

#### Response
If successful, the `payload` field will be a dictionary which contains:

| Field       | Type   | Description                                               |
|-------------|--------|-----------------------------------------------------------|
| `id`        | Number | The ID of the meme in the library                         |
| `name`      | String | The colloquial name of the meme e.g. "girl happy at mall" |
| `mediaType` | String | The media type of the meme, either "image" or "video"     |
| `fileExt`   | String | The meme's media file extension e.g. "jpg", "mp4", "png"  |
| `tags`      | Array  | The list of tags for the meme                             |
| `url`       | String | The URL to download the meme from                         |



### Edit Meme Information `(privileged)`
This allows you to edit some of the information associated with a meme in the library. This is a [privileged endpoint and requires an access token](#privileged-endpoints-and-access-tokens).

#### Call
```
POST https://reaction-meme-server.vercel.app/edit/<memeID>
```

#### Request
The request should be sent as a JSON body.

| Field  | Type   | Description                                 |
|--------|--------|---------------------------------------------|
| `name` | String | Optional, the new name of the meme          |
| `tags` | Array  | Optional, the new list of tags for the meme |

#### Response
Responds with the same data structure as [Get Meme Information](#get-meme-information).



### Browse Memes
Browse the meme library.

#### Call
```
GET https://reaction-meme-server.vercel.app/browse
```

#### Request
The request fields below should be encoded as URL parameters.

| Field      | Type   | Description                                                                                  |
|------------|--------|----------------------------------------------------------------------------------------------|
| `page`     | Number | The page of memes to retrieve                                                                |
| `per_page` | Number | The number of memes on each page. This will change the number of pages available to retrieve |


#### Response
The `payload` field of the JSON response will contain the following keys:

| Field          | Type   | Description                                                                                                                             |
|----------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `itemsPerPage` | Number | The number of items retrieved for the page. This may differ from the encoded URL parameter if less results were available for the page. |
| `page`         | Number | The page number                                                                                                                         |
| `results`      | Array  | The list of results retrieved.                                                                                                          |

Each element of `results` will have the same data structure as [Get Meme Information](#get-meme-information).



### Search For Memes
Search for memes in the library with a specific query. Queries are searched against the meme name and it's associated tags.

#### Call
```
GET https://reaction-meme-server.vercel.app/search
```

#### Request
The request fields below should be encoded as URL parameters.

| Field        | Type   | Description                                                                                                                            |
|--------------|--------|----------------------------------------------------------------------------------------------------------------------------------------|
| `query`      | String | The search query                                                                                                                       |
| `media_type` | String | Optional, Filter search results to only include this media type. Can be `"image"` or `"video"`                                         |
| `page`       | Number | Optional (default = 1), The page of search results to retrieve                                                                         |
| `per_page`   | Number | Optional (default = 10), The number of search results (memes) on each page. This will change the number of pages available to retrieve |


#### Response
Responds with the same data structure as [Browse Memes](#browse-memes).



### Add New Memes `(privileged)`
Add new memes to the meme library. This is a [privileged endpoint and requires an access token](#privileged-endpoints-and-access-tokens).

#### Call
```
POST https://reaction-meme-server.vercel.app/add
```

#### Request
The request should be a JSON body with the following fields:

| Field      | Type   | Description                                                                                                               |
|------------|--------|---------------------------------------------------------------------------------------------------------------------------|
| `name`     | String | The colloquial name of the meme e.g. "girl happy at mall"                                                                 |
| `fileExt`  | String | The meme's media file extension e.g. "jpg", "mp4", "png"                                                                  |
| `tags`     | Array  | The list of tags for the meme                                                                                             |
| `cloudID`  | String | The meme's ID in the remote storage service (is gotten from [uploading the meme media](#uploading-meme-media-privileged)) |
| `cloudURL` | String | The delivery URL to download the meme from ((is gotten from [uploading the meme media](#uploading-meme-media-privileged)) |

The `cloudID` and `cloudURL` are provided by the server after successfully uploading the meme file bytes, see [Uploading Meme Media](#uploading-meme-media-privileged)

#### Response
If successful, the server will echo the information of the new meme. Responds with the same data structure as [Get Meme Information](#get-meme-information).



### Uploading Meme Media `(privileged)`
Upload the media (image/video bytes) of a meme to the server.

This is a two-step process:
- Make an upload request to get the upload URL
- Send the file bytes to the upload URL with another request

#### Upload Request: Call
```
POST https://reaction-meme-server.vercel.app/upload-request
```

#### Upload Request: Request `(privileged)`
The JSON request body should include the following information. This is a [privileged endpoint and requires an access token](#privileged-endpoints-and-access-tokens).

| Field     | Type   | Description                                             |
|-----------|--------|---------------------------------------------------------|
| `fileExt` | String | The meme's media file extension e.g. "jpg", "mp4", "png |


#### Upload Request: Response
If successful, response `payload` field will include:

| Field       | Type   | Description                                                 |
|-------------|--------|-------------------------------------------------------------|
| `uploadURL` | String | The URL which will be used to upload the meme's file bytes. |

**Note: For security, the upload URL has an access lifetime of 3 hours. That is, a connection to the endpoint will be rejected 3-hours after the URL has been generated.**

#### Upload URL: Call & Request `(privileged)`
Make a call to the `uploadURL` returned as a response to the upload request. This is a [privileged endpoint and requires an access token](#privileged-endpoints-and-access-tokens).
```
POST <uploadURL>
```

Your request should include the meme files bytes as a data/file body.

#### Upload URL: Response
If the upload is successful, the JSON response `payload` field will include the following:

| Field      | Type   | Description                                                                             |
|------------|--------|-----------------------------------------------------------------------------------------|
| `cloudID`  | String | The ID of the meme in the remote storage service.                                       |
| `cloudURL` | String | The delivery URL from the remote storage service which the meme can be downloaded from. |


#### Upload Example
```python
import requests    
with open('belugaWhale.jpg', 'rb') as file:
    memeBinaryData = file.read()

# Enter your access token here
accessToken = "abc123"

# Make upload request
resp = requests.post('https://reaction-meme-server.vercel.app/upload-request', headers = {'Access-Token': accessToken}, json={'fileExt': 'jpg'})

# Get the upload URL from the response
uploadUrl = resp.json()['uploadURL']

# Use the upload URL to upload the meme binary dara
resp2 = requests.post(uploadUrl, headers = {'Access-Token': accessToken}, data=memeBinaryData)
```




