TRUE = 1
FALSE = 0

accessToken = RunShortcut('Get RMSVR Access Token')
serverURL = RunShortcut('Get RMSVR URL')

params = Dictionary(ShortcutInput)

memeID = AskForInput(Input.Number, prompt='Meme ID:')

res = GetContentsOfURL(f'{serverURL}/search/{memeID}', method='GET')

if RunShortcut('Check RMSVR JSON Response', input=res) is None:
    StopShortcut()

memeInfo = Dictionary(res['payload'])

for _ in range (10):
    tagsStr = CombineText( memeInfo['tags'], ',')

    for tg in memeInfo['tags']:
        matches = MatchText(r'[, ]', tg)
        if matches is not None:
            IFRESULT = f'"{tg}"'
        else:
            IFRESULT = f'{tg}'

        REPEATRESULTS.append(IFRESULT)

    verboseTagStr = CombineText(REPEATRESULTS, ',')

    prompt = f'''
        Name:
        {memeInfo['name']}
        
        Tags:
        [{tagsStr}]
        
        Media Type: 
        {memeInfo['mediaType']}
        
        ID:
        {memeInfo['id']}
    '''

    # present with menu on what they would like to do
    Menu(prompt):
        case 'Save':
            RunShorctut('Save Meme To Local Library', input={ 'id': memeInfo['id'], 'url': memeInfo['url']})
            memeSaved = TRUE
            Notification(title='Meme Saved', body=memeInfo['name'], attachment=memeMedia)
            StopShortcut()

        case 'Copy URL':
            CopyToClipboard(memeInfo['url'])
            Notification(title='URL has been copied to your clipboard', body=memeInfo['url'], attachment=memeMedia)
            StopShortcut()

        case 'View Meme':
            res = GetContentsOfURL(memeInfo['url'])
            renamedItem = SetName(res, memeInfo['name'])
            QuickLook(memeMedia)

        case 'Edit Meme':
            editDix = {
                'name': memeInfo['name'] + AskEachTime()
                'tags': tagsStr
            }

            tagsList = SplitText(editDix['tags'], ',')

            res = GetContentsOfURL(f'{serverURL}/edit/{memeInfo['id']}', 
                method='POST',
                headers = {
                    'Access-Token': accessToken,
                },
                json={
                    'name': editDix['name'],
                    'tags': tagList
                })

            if RunShortcut('Check RMSVR JSON Response', input=res) is None:
                StopShortcut()

            Alert(f'Meme {memeInfo['id']} was edited successfully', showCancel=False)

        case 'Exit':
            StopShortcut()



