import MotionEffects
import json
import sys, os

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
        self.output = "C:\Temp\MotionScriptMovie"
        self.story = []
        self.start = 0
        self.end = 0
        self.duration = 0
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
        self.output = config.get("output", self.output)

        #Build Output folder if it doesn't exist.
        if not os.path.isdir(self.output):
            os.makedirs(self.output)

        # Script
        # A list of events. Effects applied to Layers at times over durations
        self._autoIndex = 0
        story = config.get("story", [])
        for event in story:
            self.parseEvent(event)

        # Calculate Duration
        self.duration = self.end - self.start
        assert self.duration > 0, "Movie Duration is 0"

    def parseEvent(self, event):
        """ Check that all requirements of an event exist """
        #Event Name
        if not event.has_key("name"):
            prefix = "UnnamedEvent_%d"
            index = self._getAutoIndex()
            while event.has_key(prefix % index): index = self._getAutoIndex() # Create Unique Names
            event["name"] = prefix % index
        else:
            event["name"] += "_%d" % self._getAutoIndex()
        
        if not event.has_key("start"): 
            self.logger.error("No Start Time found for event %s", event["name"])
            sys.exit(1)
        elif not event.has_key("end") and not event.has_key("duration"):
            self.logger.error("No End Time or duration found for event %s", event["name"])
            sys.exit(1)
        elif not event.has_key("position"):
            self.logger.error("No position provided with event %s", event["name"])
            sys.exit(1)
        elif not event.has_key("asset"):
            self.logger.error("No Asset provided with event %s", event["name"])
            sys.exit(1)

        # Keep Track of end
        if self.end < event["end"]: self.end = event["end"]

        # Clean and Check Asset
        event["asset"] = self.parseAssets(event["asset"], event["name"])

        self.story.append(event)
        
            

    def parseAssets(self, asset, parentName=None):
        """ Parse Assets such as Effects or Images """
        if not asset.has_key("name"):
            asset["name"] = "UnnamedAsset" if parentName==None else parentName+".UnnamedAsset" 
        else:
            asset["name"] = asset["name"] if parentName==None else parentName+"."+asset["name"] 
        
        # Validate Types and Subtypes
        if not asset.has_key("type"):
            self.logger.error("Invalid type defined for asset %s", asset["name"])
            sys.exit(1)
        if not asset.has_key("subtype"):
            self.logger.error("subtype not defined for asset in %s", asset["name"])
            sys.exit(1)
        
        if asset["type"] == 'effect':
            if asset["subtype"] not in MotionEffects.effects.keys():
                self.logger.error("Invalid subtype %s defined for asset %s", asset["subtype"], asset["name"])
                sys.exit(1)
            else:
                asset["asset"] = self.parseAssets(asset=asset["asset"], parentName=asset["name"])
        elif asset["type"] == 'primative':
            if asset["subtype"] == 'image':
                if not os.path.isfile(asset["path"]):
                    self.logger.error("Image File does not exist - %s(%s)", asset["path"])
                    test = open("RedBall.png", "r")
                    sys.exit(1)
            elif asset["subtype"] == 'animation':
                if not os.path.isdir(asset["path"]):
                    self.logger.error("Animation Path does not exist - %s", asset["path"])
                    sys.exit(1)
        else:
            self.logger.error("Invalid type %s defined for asset %s",asset["type"],  asset["name"])

        return asset
