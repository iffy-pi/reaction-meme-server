from enum import Enum
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

def getMediaTypeForExt(fileExt:str) -> MemeMediaType:
    fileExt = fileExt.lower().replace('.', '')
    if fileExt in VIDEO_EXTENSIONS:
        return MemeMediaType.VIDEO
    elif fileExt in IMAGE_EXTENSIONS:
        return MemeMediaType.IMAGE
    else:
        return MemeMediaType.UNKNOWN

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
