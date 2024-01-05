# Set to "prod" for production URL
# Set to "dev" for development URL
envKey = "prod"

if envKey == 'dev':
	ShowAlert('Using dev URL!')
	IFRESULT = 'http://192.168.2.101:5000'
else:
	IFRESULT = 'https://reaction-meme-server-api.vercel.app'

StopShortcut(output=IFRESULT)