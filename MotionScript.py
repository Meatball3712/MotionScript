# Main Build Function

import os, traceback
import argparse
import json
from MotionLogger import buildDefaultLogger
import MotionLayer
from PIL import Image

# How to Assert
#assert type("1") is int, "Type is not integer"

class MotionScriptConfig:
    """Instructions for building a movie"""
    def __init__(self, configFile, **kwargs):
        self.configFile = configFile
        self.logger = (kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger()).getChild("Config")
        self.valid = True
        self.screenSize = (1920,1080)
        self.framerate = 24
        self.outPath = "C:\Temp\MotionScriptMovie"
        self.layers = []
        self.story = {}

        self._autoIndex = 0
        self._layerNames = []

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
        self.screenSize = config.get("screenSize", self.screenSize)
        self.framerate = config.get("framerate", 24)
        
        # Layers
        for layer in config.get("layers", []):
            self.parseLayer(layer)

        # Script
        # A list of events. Effects applied to Layers at times over durations
        self._autoIndex = 0
        story = config.get("story", [])
        for event in story:
            self.parseEvent(self, event)


    def parseLayer(self, layer):
        """Check an individual layer's config"""
        # Minimum requirements for a layer.

        # Layer Name - for identification purposes
        if not layer.has_key("name"):
            layer["name"] = "UnnamedLayer_%d" % self._getAutoIndex()
        self._layerNames.append(layer["name"])

        # Type - either image or animation
        if not layer.has_key("type") or layer["type"] not in ('image', 'animation'):
            self.logger.error("Invalid type defined for layer %s", layer["name"])
            raise AttributeError("Bad Layer Config")

        # Check Path
        if not layer.has_key("path"):
            self.logger.error("No Path Supplied in Layer Config - %s", layer["name"])
            return False
        elif layer["type"] == "image" and not os.path.isfile(layer["path"]):
            self.logger.error("Image File does not exist - %s", layer["path"])
            return False
        elif layer["type"] == "animation" and not os.path.isdir(layer["path"]):
            self.logger.error("Animation Path does not exist - %s", layer["path"])

        self.layers.append(layer)
        return True

    def parseEvent(self, event):
        """ Check that all requirements of an event exist """
        #Event Name
        if not event.has_key("name"):
            event["name"] = "UnnamedEvent_%d" % self._getAutoIndex()

        if not event.has_key("layerName") or event["layerName"] not in self._layerNames:
            self.logger.error("Layer Name (%s) not defined for event %s", % event.get("layerName", ""), event["name"])
            raise AttributeError("Bad Event Config")
        
        elif not event.has_key("start"): 
            self.logger.error("No Start Time found for event %s", event["name"])
            raise AttributeError("Bad Event Config")
        
        elif not event.has_key("end"):
            self.logger.error("No End Time found for event %s", event["name"])
            raise AttributeError("Bad Event Config")

        elif not event.has_key("effect"):
            self.logger.error("No effect set for event %s", event["name"])
            raise AttributeError("Bad Event Config")

        else:
            # Optional - check event specific attributes
            if not self.story.has_key(event["start"])
                self.story.append(event)
            


class MotionScript:
    """Build Movie from assets and instructions"""
    def __init__(self, **kwargs):
        # Check valid config
        assert kwargs.has_key("config"), "config parameter not supplied"
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger()
        self.config = MotionScriptConfig(kwargs["config"], logger=self.logger)

        self.layers = []
        self.stage = []
        self.logger.info("MotionScript initialised")
        self.build(self)

    def build(self):
        self.logger.info("Building Movie...")

        self.screen = Image.new
        for layer in self.config.layers:
            if layer["type"] == "image":
                self.layers.append(MotionLayer.ImageLayer(**layer))
            else:
                self.layers.append(MotionLayer.AnimationLayer(**layer))


        for element in self.config.story:
            pass

    def animate(self):
        for frame in self.movieLength:
            events = self.story.get(frame, []) # Get all new events for this moment, and process the stage.
            

    def exitStage(self, layer):
        """ Remove Layer from stage (No longer processing each frame) """
        pass

    def enterStage(self, layer):
        """ Add Layer to stage for processing next frame increment """
        pass



if __name__ == "__main__":
    ### Command Line Arguments ###
    parser = argparse.ArgumentParser(description="Hadoop ETL")
    parser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help= "Perform debug testing instead of actually submitting.")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help= "Run complete, but show debug messages and log to console")
    parser.add_argument("config", help= "Build File")
    args = vars(parser.parse_args())
    debug = args["debug"]
    verbose = args["verbose"]

    logger = buildDefaultLogger(verbose, debug)
    MS = MotionScript(logger=logger, **args)