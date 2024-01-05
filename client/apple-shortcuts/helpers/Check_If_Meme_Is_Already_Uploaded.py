mediaItem = ShortcutInput
foundPhoto = FindPhotos('All Photos', filterAllAreTrue(album='Reaction Memes', name=File(mediaItem).Name), limit=1)

if foundPhoto is None:
	savedPhoto = SaveToPhotoAlbum(mediaItem, 'Reaction Memes')
	IFRESULT = GetDetailsOfImages('Name', savedPhoto)
else:
	# Is already in the album
	# Check if it is in local lib
	file = GetFile(From='Shortcuts', 'ReactionMemeServer/localLib.json', errorIfNotFound=False)
	localLib = Dictionary(file)


	results = FilterFiles(localLib.Values, filter(Name=File(mediaItem).Name))
	if results is not None:
		Alert('Meme has already been uploaded to the Reaction Meme Server. Do you still want to continue?')


	IFRESULT = GetDetailsOfFile('Name', mediaItem)

StopShortcut(output=IFRESULT)