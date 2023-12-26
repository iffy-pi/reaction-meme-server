from enum import Enum
VIDEO_EXTENSIONS = ('mov', 'mp4', 'webm', 'avi', '3g2', 'mpeg' '3gp', 'ts', 'ogv')
IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'heic', 'tiff', 'webp', 'ico', 'tif', 'svg', 'bmp')

class MemeMediaType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    UNKNOWN = 'unknown'

def getMediaTypeForExt(fileExt:str) -> MemeMediaType:
    fileExt = fileExt.lower().replace('.', '')
    if fileExt in VIDEO_EXTENSIONS:
        return MemeMediaType.VIDEO
    elif fileExt in IMAGE_EXTENSIONS:
        return MemeMediaType.IMAGE
    else:
        return MemeMediaType.UNKNOWN

def getMediaTypeFromValue(st:str) -> MemeMediaType:
    types = [
        MemeMediaType.IMAGE,
        MemeMediaType.VIDEO,
        MemeMediaType.UNKNOWN
    ]
    st = st.lower()
    for t in types:
        if st ==t.value:
            return t

    raise Exception(f"Unknown type for string '{st}'")