import MotionEffects

class InvalidMotionScript(Exception):
    pass

class MotionScriptConfig:
    """Instructions for building a movie"""
    def __init__(self, configFile, **kwargs):
        self.configFile = configFile
        self.logger = (kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger()).getChild("Config")
        self.valid = True
        self.size = (1920,1080)
        self.framerate = 24
        self.outPath = "C:\Temp\MotionScriptMovie"
        self.story = []

        self._autoIndex = 0
        self.load(configFile)

    def _getAutoIndex(self):
        temp = self._autoIndex
        self._autoIndex += 1
        return temp

    def load(self, configFile):
        self.logger.info("Loading Config File %s", self.configFile)
        with open(configFile) as f:
            # Parse the config file
            config = json.load(f)

        # Begin Checks.
        self.size = config.get("size", self.size)
        self.framerate = config.get("framerate", 24)

        # Script
        # A list of events. Effects applied to Layers at times over durations
        self._autoIndex = 0
        story = config.get("story", [])
        for event in story:
            self.parseEvent(self, event)

    def parseEvent(self, event):
        """ Check that all requirements of an event exist """
        #Event Name
        if not event.has_key("name"):
            prefix = "UnnamedEvent_%d"
            index = self._getAutoIndex()
            while event.has_key(prefix % index): index = self._getAutoIndex() # Create Unique Names
            event["name"] = prefix % index
        
        if not event.has_key("start"): 
            self.logger.error("No Start Time found for event %s", event["name"])
            raise AttributeError("Bad Event Config")
        elif not event.has_key("end") and not event.has_key("duration"):
            self.logger.error("No End Time or duration found for event %s", event["name"])
            raise AttributeError("Bad Event Config")
        elif not event.has_key("asset"):
            self.logger.error("No Asset provided with event %s", event["name"])
            raise AttributeError("Bad Event Config")

        # Clean and Check Asset
        event["asset"] = self.parseAssets(event["asset"], event["name"])

        self.story.append(event)
        
            

    def parseAssets(self, asset, parentName=None):
        """ Parse Assets such as Effects or Images """
        if not asset.has_key("name"):
            asset["name"] = "UnnamedAsset" if parent==None else parent["name"]+".UnnamedAsset" 
        
        # Type - either primative or effect
        if not asset.has_key("type") or asset["type"] not in ('primative', 'effect'):
            self.logger.error("Invalid type defined for asset %s", asset["name"])
            raise AttributeError("Bad Asset Config")

        if not asset.has_key("subtype") or asset["subtype"] not in ('image', 'animation') or asset["subtype"] not in Effects.effects.keys():
            self.logger.error("Invalid subType defined for asset %s", asset["name"])
            raise AttributeError("Bad Asset Config")

        # Check Path if image.
        if asset.has_key("type") in ('image', 'animation') and not asset.has_key("path"):
            self.logger.error("No Path Supplied in Asset Config - %s", asset["name"])
            raise AttributeError("Bad Event Config")
            if asset["type"] == "image" and not os.path.isfile(asset["path"]):
                self.logger.error("Image File does not exist - %s", asset["path"])
                raise AttributeError("Bad Event Config")
            elif asset["type"] == "animation" and not os.path.isdir(asset["path"]):
                self.logger.error("Animation Path does not exist - %s", asset["path"])
                raise AttributeError("Bad Event Config")
        else:
            asset["asset"] = self.parseAssets(asset=asset["asset"], name=asset["name"])

        return asset
