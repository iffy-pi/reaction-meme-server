
if ShortcutInput is not None:
	IFRESULT = ShortcutInput
else:
	photoMedia = SelectPhotos()
	mediaType = GetDetailsOfImages('Media Type', photoMedia)
	if mediaType == 'Video':
		IFRESULT1 = EncodeMedia(photoMedia)
	else:
		IFRESULT1 = GetVariable(photoMedia)

	IFRESULT = IFRESULT1

mediaItem = IFRESULT

ShowResult(mediaItem)

accessToken = RunShortcut('Get RMSVR Access Token')
serverURL = '...'

# Save media item to reaction memes if not already
savedPhotoName = RunShortcut('Check If Meme Is Uploaded', input=mediaItem)


ext = GetDetailsOfFile('File Extension', mediaItem)
information = {
	'name': AskEachTime(),
	'tags': '',
	'fileExt': ext
}

tags = SplitText(information['tags'], ',')

# First do the upload request
res = GetContentsOfURL(f'{serverURL}/upload-request', method='GET', headers={'Access-Token': accessToken})

if RunShortcut('Check RMSVR JSON Response', input=res) is None:
	StopShortcut()

reqResp = Dictionary(res)

# Then upload the meme to the upload URL
uploadURL = reqResp['payload.uploadURL']

res = GetContentsOfURL(uploadURL, method='POST', headers={'Access-Token': accessToken}, requestBody='Form', 
							body={
								'file': File(mediaItem)
								'fileExt': Text(fileExt)
								} )

if RunShortcut('Check RMSVR JSON Response', input=res) is None:
	StopShortcut()

uploadRes = Dictionary(res)

res = GetContentsOfURL(f'{serverURL}/add', method='POST', headers={'Access-Token': accessToken}, json={
		'name': information['name'],
		'tags': tags,
		'fileExt': information['fileExt'],
		'cloudID': uploadRes['payload.cloudID'],
		'cloudURL': uploadRes['payload.cloudURL']
	})


if RunShortcut('Check RMSVR JSON Response', input=res) is None:
	StopShortcut()

addRes = Dictionary(res)

RunShortcut('Save Meme To Local Library', input = {
		'id': addRes['payload.id'],
		'photo_name' : savedPhotoName
	})


text = f'''
ID: {addRes['payload.id']}
Name: "{addRes['payload.name']}"
URL: {addRes['payload.url']}
'''

Notification(title='Your meme has been uploaded', body=text, attachment=mediaItem)



