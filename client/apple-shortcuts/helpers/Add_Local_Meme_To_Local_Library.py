params = Dictionary(ShortcutInput)
memeID = params['id']
photoName = params['photo_name']

localMemePhoto = FindPhotos('All Photos', filterAllAreTrue(album='Reaction Memes', name=photoName), limit=1)

if GetDetailsOfImages('Album', localMemePhoto) != 'Reaction Memes':
	SaveToPhotoAlbum(localMemePhoto, 'Reaction Memes')

file = GetFile(From='Shortcuts', 'ReactionMemeServer/localLib.json', errorIfNotFound=False)
localLib = Dictionary(file)
localLib[memeID] = localMemePhoto.Name
SaveFile(localLib, To='Shortcuts', 'ReactionMemeServer/localLib.json', overwrite=True)