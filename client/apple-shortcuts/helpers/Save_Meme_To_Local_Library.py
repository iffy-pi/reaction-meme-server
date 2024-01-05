# Shortcut that keeps track of the memes I've already saved
# Memes already in my camera roll will just be moved to the front

params = Dictionary(ShortcutInput)
memeID = params['id']
memeURL = params['url']

file = GetFile(From='Shortcuts', 'ReactionMemeServer/localLib.json', errorIfNotFound=False)
localLib = Dictionary(file)


localImgName = localLib[memeID]
if localImgName is not None:
	localMemePhoto = FindPhotos('All Photos', filterAllAreTrue(album='Reaction Memes', name=localImgName), limit=1)
	# Encoding media so that .mov files are interpreted as videos instead of JPEG images
	if localMemePhoto is not None:
		localMeme = EncodeMedia(localMemePhoto)


if localMeme is None:
	# if no local meme, download the meme to reaction
	memeMedia = GetContentsOfURL(memeURL)
	SaveToPhotoAlbum(memeMedia, 'Reaction Memes')

else:
	# There is a local meme, delete it and resave it
	tempLocal = SaveFile(localMeme, To='Shortcuts/ReactionMemeServer/temp', overwrite=True)
	DeletePhotos(localMemePhoto)
	SaveToPhotoAlbum(tempLocal, 'Reaction Memes')


# Update our local lib to match
savedMeme = FindPhotos('All Photos', filter(album='Reaction Memes'), sortBy='Creation Date', order='Latest First', limit=1)
savedName = GetDetailsOfFile('Name', savedMeme)

localLib[memeID] = savedName

# Clear temp file created
contents = GetContentsOfFolder(Folder('Shortcuts/ReactionMemeServer/temp'))
if contents is not None:
	DeleteFiles(contents)

# save local lib
SaveFile(localLib, To='Shortcuts', 'ReactionMemeServer/localLib.json', overwrite=True)
