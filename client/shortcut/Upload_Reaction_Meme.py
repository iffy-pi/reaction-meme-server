
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
reqResp = GetContentsOfURL(f'{serverURL}/upload-request', method='POST', headers={'Access-Token': accessToken}, json={
		'fileExt': information['fileExt']
	})

if reqResp['error'] is not None:
	text = f'''
	An error occured with the request:
	{reqResp['error_message']}
	'''
	QuickLook(text)
	StopShortcut()

# Then upload the meme to the upload URL
uploadURL = reqResp['payload.uploadURL']

uploadRes = GetContentsOfURL(uploadURL, method='POST', headers={'Access-Token': accessToken}, file=mediaItem )

if uploadRes['error'] is not None:
	text = f'''
	An error occured with the request:
	{uploadRes['error_message']}
	'''
	QuickLook(text)
	StopShortcut()


addRes = GetContentsOfURL(f'{serverURL}/add', method='POST', headers={'Access-Token': accessToken}, json={
		'name': information['name'],
		'tags': tags,
		'fileExt': information['fileExt'],
		'cloudID': uploadRes['payload.cloudID'],
		'cloudURL': uploadRes['payload.cloudURL']
	})

if addRes['error'] is not None:
	text = f'''
	An error occured with the request:
	{addRes['error_message']}
	'''
	QuickLook(text)
	StopShortcut()


text = f'''
ID: {addRes['payload.id']}
Name: "{addRes['payload.name']}"
URL: {addRes['payload.url']}
'''

Notification(title='Your meme has been uploaded', body=text, attachment=mediaItem)



