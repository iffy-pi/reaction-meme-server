# If bad response, outputs nothing
# If good response, outputs the respons

title =  'Request Error'
resp = Dictionary(ShortcutInput)

if resp is None:
	ShowAlert('The server did not send a response', title=title)
	StopShortcut()

if resp['error'] is not None:
	ShowAlert(f'''
		An error occured with the request:
		{resp['error_message']}
		'''
		title=title)
	StopShortcut()

StopShortcut(output=resp)