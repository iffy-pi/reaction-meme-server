import base64
from io import BytesIO
from PIL import Image

class ThumbnailMaker:
    DEFAULT_SIZE = (100, 100)
    DEFAULT_FORMAT = 'jpeg'
    @staticmethod
    def makeBase64Thumbnail(imageBytes:bytes, tbSize=None, tbFrmt=None) -> str:
        if tbSize is None:
            tbSize = ThumbnailMaker.DEFAULT_SIZE
        if tbFrmt is None:
            tbFrmt = ThumbnailMaker.DEFAULT_FORMAT

        image = Image.open(BytesIO(imageBytes))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail(tbSize)
        buffered = BytesIO()
        image.save(buffered, format=tbFrmt)
        img_str = base64.b64encode(buffered.getvalue())
        return img_str.decode()


