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

text = f'''
    Enter meme search query.
    To cancel, enter an empty search query.
'''

query = AskForInput(Input.Text, prompt=text)

# Check if the query is empty
updatedText = query.ReplaceText(' ', '')
if updatedText is None:
    StopShortcut()

searchMediaType = "all"

for _ in range (50):
    if searchExit == FALSE:
        searchItems = {}

        # make the query and savethe items
        url = URL(f"{serverURL}/search?query={query}&page={pageNo}&per_page={resultsPerPage}&media_type={searchMediaType}")
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
            N;CHARSET=utf-8:Apply search filter
            ORG:Filter for specific media type or other items
            NOTE;CHARSET=UTF-8:Filter
            {searchIcon}
            END:VCARD

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:New Search
            ORG: Try a different query
            NOTE;CHARSET=UTF-8:New
            {searchIcon}
            END:VCARD

            BEGIN:VCARD
            VERSION:3.0
            N;CHARSET=utf-8:Exit
            ORG:No food will be selected
            NOTE;CHARSET=UTF-8:Cancel
            {searchIcon}
            END:VCARD
        '''

        renamedItem = SetName(text, 'vcard.vcf')
        contacts = GetContacts(renamedItem)

        text = f'''
        "{query}" Search Results ⸱ Page {pageNo}
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
            memeMedia = GetContentsOfURL(item['url'])

            QuickLook(memeMedia)

            memeSaved = FALSE

            # present with menu on what they would like to do
            Menu('What would you like to do?'):
                case 'Save Meme':
                    SaveToPhotoAlbum(memeMedia, 'Reaction Memes')
                    memeSaved = TRUE
                    Notification(title='Meme Saved', body=item['name'], attachment=memeMedia)
                
                case 'Back To Search':
                    pass

                case 'Exit':
                    StopShortcut()

            # if saved then present with secondary options
            if memeSaved == TRUE:
                Menu('What would you like to do?'):
                    case 'Back To Search':
                        pass

                    case 'New Search':
                        RunShorctut('Search Reaction Memes')
                        StopShortcut()

                    case 'Exit':
                        StopShortcut()



