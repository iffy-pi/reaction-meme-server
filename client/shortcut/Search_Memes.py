
accessToken = RunShortcut('Get RMSVR Access Token')
serverURL = '...'
mediaItem = ShortcutInput

ext = GetDetailsOfFile('File Extension', mediaItem)
information = {
	'name': AskEachTime(),
	'tags': '',
	'fileExt': ext
}

memeAddURL = f'{serverURL}/memes/add'

tags = SplitText(information['tags'], ',')

addRes = GetContentsOfURL(memeAddURL, method='POST', headers={'Access-Token': accessToken}, json={
		'name': information['name'],
		'tags': tags,
		'fileExt': information['fileExt']
	})

if addRes['error'] is not None:
	text = f'''
	An error occured with the request:
	{addRes['error']}
	'''
	QuickLook(text)
	StopShortcut()


uploadURL = addRes['payload.uploadURL']

uploadRes = GetContentsOfURL(uploadURL, method='POST', headers={'Access-Token': accessToken}, file=mediaItem )

if uploadRes['error'] is not None:
	text = f'''
	An error occured with the request:
	{uploadRes['error']}
	'''
	QuickLook(text)
	StopShortcut()

text = f'''
ID: {addRes['payload.id']}
Name: "{addRes['payload.name']}"
URL: {uploadRes['payload.url']}
'''

Notification(title='Your meme has been uploaded', body=text, attachment=mediaItem)



