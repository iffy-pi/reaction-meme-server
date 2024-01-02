
accessToken = RunShortcut('Get RMSVR Access Token')
serverURL = '...'
mediaItem = ShortcutInput

ext = GetDetailsOfFile('File Extension', mediaItem)
information = {
	'name': AskEachTime(),
	'tags': '',
	'fileExt': ext
}

tags = SplitText(information['tags'], ',')

# First do the upload request
res = GetContentsOfURL(f'{serverURL}/upload-request', method='POST', headers={'Access-Token': accessToken}, json={
		'fileExt': information['fileExt']
	})

if RunShortcut('Check RMSVR JSON Response', input=res) is None:
	StopShortcut()

reqResp = Dictionary(res)

# Then upload the meme to the upload URL
uploadURL = reqResp['payload.uploadURL']

res = GetContentsOfURL(uploadURL, method='POST', headers={'Access-Token': accessToken}, file=mediaItem )

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

text = f'''
ID: {addRes['payload.id']}
Name: "{addRes['payload.name']}"
URL: {addRes['payload.url']}
'''

Notification(title='Your meme has been uploaded', body=text, attachment=mediaItem)



