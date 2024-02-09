from enum import Enum
import mimetypes
VIDEO_EXTENSIONS = ('mov', 'mp4', 'webm', 'avi', '3g2', 'mpeg' '3gp', 'ts', 'ogv')
IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'heic', 'tiff', 'webp', 'ico', 'tif', 'svg', 'bmp')

class MemeMediaType(Enum):
    UNKNOWN = 0
    IMAGE = 1
    VIDEO = 2

STRING_MAP =  {
    MemeMediaType.UNKNOWN : 'unknown',
    MemeMediaType.IMAGE : 'image',
    MemeMediaType.VIDEO : 'video',
}

def getMediaTypeForMimeType(mime:str) -> MemeMediaType:
    if mime.startswith('image/'):
        return MemeMediaType.IMAGE

    elif mime.startswith('video/'):
        return MemeMediaType.VIDEO

    else:
        return MemeMediaType.UNKNOWN

def getMediaTypeForExt(fileExt:str) -> MemeMediaType:
    fileExt = fileExt.lower().replace('.', '')
    mime = mimetypes.guess_type(f'f.{fileExt}')[0]
    if mime is None:
        return MemeMediaType.UNKNOWN

    return getMediaTypeForMimeType(mime)


def isValidMediaType(fileExt:str=None, mimeType:str=None) -> bool:
    if fileExt is None and mimeType is None:
        raise Exception('No arguments provided')

    mt = None
    if fileExt is not None:
        mt = getMediaTypeForExt(fileExt)
    elif mimeType is not None:
        mt = getMediaTypeForMimeType(mimeType)

    return mt != MemeMediaType.UNKNOWN

def stringToMemeMediaType(st:str) -> MemeMediaType:
    types = list(MemeMediaType.__members__.values())
    st = st.lower()
    for t in types:
        if st == STRING_MAP[t]:
            return t

    raise Exception(f"Unknown type for string '{st}'")

def memeMediaTypeToString(t: MemeMediaType) -> str:
    return STRING_MAP[t]

def memeMediaTypeToInt(t: MemeMediaType) -> int:
    return t.value

def intToMemeMediaType(i: int) -> MemeMediaType:
    types = list(MemeMediaType.__members__.values())
    for t in types:
        if i == t.value:
            return t
