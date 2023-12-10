import json
import os

from apiutils.MemeManagement.MemeUploaderInterface import MemeUploaderInterface
from apiutils.configs.ServerConfig import ServerConfig


class LocalStorageUploader(MemeUploaderInterface):
    """
    Uploads to devenv/localmemes
    """
    def __init__(self, configJSONFilePath:str, memeDir:str, addUploadedFlag=False):
        """
        Initializes the local storage uploader
        :param configJSONFilePath: The path to the config JSON file, this JSON file must contain a nextID key
        :param memeDir: The path to the directory where all the memes are stored.
        :param addUploadedFlag : Set to true and memes uploaded using the uploader object will be named meme_<id>_uploaded, instead of just meme_<id>

        The class works in the following way:
            The config file is used to keep track of the next ID to assign to a newly uploaded meme
            When a new meme is uploaded, it is written to the memeDir with the naming format meme_{id}.{fileExt} (or with uploaded appended as mentioned above)
            The config file is also updated when a new meme is added, the value of next ID is incremented.
        """
        self.configFile = configJSONFilePath
        self.memeDir = memeDir


    def uploadMedia(self, mediaBinary:bytes, fileExt) -> tuple[str, str]:
        # get the next id
        with open(self.configFile, "r") as file:
            config = json.load(file)

        nextId = int(config["nextID"])

        # save the binary to the location
        filename = f"meme_{nextId}_uploaded.{fileExt}"
        with open(os.path.join(self.memeDir, filename), "wb") as file:
            file.write(mediaBinary)

        # update nextId
        config["nextID"] = nextId+1

        with open(self.configFile, "w") as file:
            json.dump(config, file, indent=4)

        # make the url
        cloudURL = f"http://127.0.0.1:5001/local/meme/{nextId}"

        # return the ID and url
        return str(nextId), cloudURL