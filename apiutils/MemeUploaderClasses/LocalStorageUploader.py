import json
import os

from apiutils.MemeManagement.MemeUploaderInterface import MemeUploaderInterface
from apiutils.configs.ServerConfig import ServerConfig


class LocalStorageUploader(MemeUploaderInterface):
    """
    Uploads to devenv/localmemes
    """
    def __init__(self):
        self.configFile = os.path.join(ServerConfig.PROJECT_ROOT, "devenv", "localmemes", "config.json")
        self.memeDir = os.path.join(ServerConfig.PROJECT_ROOT, "devenv", "localmemes")


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