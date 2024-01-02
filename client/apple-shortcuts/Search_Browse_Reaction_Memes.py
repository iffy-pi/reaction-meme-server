TRUE = 1
FALSE = 0

accessToken = RunShortcut('Get RMSVR Access Token')
serverURL = '...'


# vcard base64 photo icons
servingSizeIcon = # ... , see servingSizeIcon.txt
forwardIcon = # forwardIcon.txt
backwardIcon = # backwardIcon.txt
searchIcon = # searchIcon.txt
cancelIcon = # cancelIcon.txt
verifIcon = '★'

resultsPerPage = 7
searchExit = FALSE
pageNo = 1
browseMemes = FALSE


params = Dictionary(ShortcutInput)
text = f'{params['function']}'


if text == 'browse':
    browseMemes = TRUE


if browseMemes == TRUE:
    IFRESULT = f'{serverURL}/browse?'
else:
    text = f'''
        Enter meme search query.
        To cancel, enter an empty search query.
    '''

    query = AskForInput(Input.Text, prompt=text)

    # Check if the query is empty
    updatedText = query.ReplaceText(' ', '')
    if updatedText is None:
        StopShortcut()

    IFRESULT = f'{serverURL}/search?query={query}&'\

baseURL = IFRESULT

searchMediaType = "all"

for _ in range (50):
    if searchExit == FALSE:
        searchItems = {}

        # make the query and savethe items
        url = URL(f"{baseURL}page={pageNo}&per_page={resultsPerPage}&media_type={searchMediaType}")
        res = Dictionary(GetContentsOfURL(URL))

        for repeatItem in res['payload.results']:
            # cache the item away using its id
            item = repeatItem
            itemId = item['id']
            searchItems[ itemId ] = item

            # construct the vcard 
            tags = CombineText(item['tags'], ',')
            text = f'''
            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=UTF-8:{item['name']}
            ORG;CHARSET=UTF-8:{tags}
            NOTE;CHARSET=UTF-8:{itemId}
            END:VCARD
            '''
            
            REPEATRESULTS.append(text)
        
        itemCards = REPEATRESULTS

        if browseMemes == TRUE:
            IFRESULT = {
                'search': 'Search For Meme...',
                'exit': 'Exit Browsing',
                'back': 'Back To Browsing'
            }
        else:
            IFRESULT = {
                'search': 'New Search',
                'exit': 'Exit Search',
                'back': 'Back To Search'
            }
        buttonLabels = IFRESULT   

        # Add next, previous, new search and cancel search buttons
        nextPage = pageNo+1
        prevPage = nextPage-2
        

        text = f'''
            {itemCards}

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:Next Page
            ORG: Page {nextPage}
            NOTE;CHARSET=UTF-8:Next
            {forwardIcon}
            END:VCARD

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:Previous Page
            ORG: Page {prevPage}
            NOTE;CHARSET=UTF-8:Prev
            {backwardIcon}
            END:VCARD

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:Filter Memes
            ORG:Filter for specific media type or other items
            NOTE;CHARSET=UTF-8:Filter
            {searchIcon}
            END:VCARD

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:{buttonLabels['search']}
            ORG: Try a different query
            NOTE;CHARSET=UTF-8:New
            {searchIcon}
            END:VCARD

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:Exit
            ORG:{buttonLabels['exit']}
            NOTE;CHARSET=UTF-8:Cancel
            {searchIcon}
            END:VCARD
        '''

        renamedItem = SetName(text, 'vcard.vcf')
        contacts = GetContacts(renamedItem)

        if browseMemes == TRUE:
            IFRESULT = 'Meme Library'
        else:
            IFRESULT = f'"{query}" Search Results'
        
        text = f'''
            Reaction Meme Server
            {IFRESULT} ⸱ Page {pageNo}
        '''

        chosenItem = ChooseFrom(contacts, prompt=text)
        isControlItem = FALSE

        if chosenItem.Notes == 'Next':
            isControlItem = TRUE
            pageNo = pageNo + 1

        if chosenItem.Notes == 'Prev':
            isControlItem = TRUE
            pageNo = pageNo - 1
            if pageNo == 0:
                Alert("This is the first page of the search!")
                pageNo = pageNo + 1

        if chosenItem.Notes == 'Filter':
            isControlItem = TRUE
            Menu('Select Filter'):
                case 'Images Only':
                    MENURESULT = "images"
                case 'Videos Only':
                    MENURESULT = "video"
                case 'All Types':
                    MENURESULT = "all"

            searchMediaType = MENURESULT
            pageNo = 1

        if chosenItem.Notes == 'New':
            isControlItem = TRUE
            RunShorctut('Search Reaction Memes')
            StopShortcut()

        if chosenItem.Notes == 'Cancel':
            isControlItem = TRUE
            StopShortcut()
        
        if isControlItem == FALSE:
            # then its not a control item
            itemId = chosenItem.Notes
            item = searchItems[ itemId ]

            # Download the meme and show the user
            res = GetContentsOfURL(item['url'])
            memeMedia = SetName(res, item['name'])

            QuickLook(memeMedia)

            viewMemeLoopExit = FALSE
            memeSaved = FALSE

            for _ in range(15):
                if viewMemeLoopExit == FALSE:
                    res = GetContentsOfURL(f'{serverURL}/search/{item['id']}', method='GET')
                    memeInfo = Dictionary(res['payload'])
                    tagsStr = CombineText( memeInfo['tags'], ',')

                    for it in memeInfo['tags']:
                        matches = MatchText(r'[, ]', it)
                        if matches is not None:
                            IFRESULT = f'"{it}"'
                        else:
                            IFRESULT = f'{it}'

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
                            Notification(title='Meme Saved', body=item['name'], attachment=memeMedia)
                            StopShortcut()

                        case 'Copy URL':
                            CopyToClipboard(memeInfo['url'])
                            Notification(title='URL has been copied to your clipboard', body=memeInfo['url'], attachment=memeMedia)
                            StopShortcut()

                        case 'View Meme':
                            renamedItem = SetName(memeMedia, memeInfo['name'])
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

                            if res['error'] is not None:
                                text = f'''
                                An error occured with the request:
                                {res['error_message']}
                                '''
                                QuickLook(text)
                                StopShortcut()

                            Alert(f'Meme {memeInfo['id']} was edited successfully', showCancel=False)

                        
                        case f'{buttonLabels['back']}':
                            viewMemeLoopExit = TRUE

                        case 'Exit':
                            StopShortcut()

            # if saved then present with secondary options
            if memeSaved == TRUE:
                Menu('What would you like to do next?'):
                    case f'{buttonLabels['back']}':
                        pass

                    case 'New Search':
                        RunShorctut('Search Reaction Memes')
                        StopShortcut()

                    case 'Exit':
                        StopShortcut()



