# Main Build Function

import os, traceback
import argparse
import json
from MotionLogger import buildDefaultLogger
import MotionPrimative
import MotionEffects
from PIL import Image
from MotionScriptConfig import *

assetTypes = ("image", "animation")
class MotionEvent:
    def __init__(self, eventConfig):
        self.name = eventConfig["name"]
        self.start = eventConfig["start"]
        self.end = eventConfig["end"]
        self.asset = buildAsset(eventConfig["asset"])

    def buildAssets(self, assetConfig):
        # Recursively build assets.
        if assetConfig["type"]  == "image":
            asset = MotionPrimative.ImageLayer(size=self.config.size, **layer)
        elif assetConfig["type"] == "animation":
            asset = MotionPrimative.AnimationLayer(size=self.config.size, **layer)
        else:
            asset["asset"] = self.buildAssets(asset["asset"])
            MotionEffects.buildEffect(asset)

            

                


class MotionScript:
    """Build Movie from assets and instructions"""
    def __init__(self, **kwargs):
        # Check valid config
        assert kwargs.has_key("config"), "config parameter not supplied"
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger()
        self.config = MotionScriptConfig(kwargs["config"], logger=self.logger)
        if not self.config.valid:
            raise InvalidMotionScript("Config invalid")
        else:
            self.logger.info("Config Validated")

        self.size = self.config.get("size", (1920,1080))
        self.layers = {}
        self.timeline = {}
        self.stage = []
        self.logger.info("MotionScript initialised")
        self.build(self)

    def build(self):
        self.logger.info("Building Movie...")
        # Build Timeline
        for event in self.config.story:
            # Build Assets
            event["asset"]
            if not self.timeline.has_key(event["start"]):
                self.timeline[event["start"]] = []
            self.timeline[event["start"]].append(event)

            if not self.timeline.has_key(event["end"]):
                self.timeline[event["end"]] = []
            self.timeline[event["end"]].append(event)

        # Build Stage
        self.updateStage()

    def animate(self):
        for frame in xrange(self.movieLength):
            screen = Image.new(size=self.size, mode="RGBA",color=(0,0,0,255))

            # Build list of layers by sorted z_index
            layerDepths = {}
            for layer in self.stage:
                if not layerDepths.has_key(layer.position[2]):
                    layerDepths[layer.position[2]] = []
                layerDepths[layer.position[2]].append(layer)

            ordered = layerDepths.keys()
            ordered.sort()
            for index in ordered:
                for layer in layerDepths[index]:
                    screen.paste(layer.getNextImage())
                
            events = self.timeline.get(frame, []) # Get all new events for this moment, and process the stage.
            for event in events:
                # Exit any elements that have finished
                if event["end"] > frame:
                    self.exitStage(event["layerName"])
                # Enter any new elements that are beginning
                if event["start"] >= frame and event["end"] < frame:
                    self.enterStage(event["layerName"])
            
    def updateStage(self, frame=0):
        events = self.timeline.get(frame, []) # Get all new events for this moment, and process the stage.
        for event in events:
            # Exit any elements that have finished
            if event["end"] > frame:
                self.exitStage(event["layerName"])
            # Enter any new elements that are beginning
            if event["start"] >= frame and event["end"] < frame:
                self.enterStage(event["layerName"])

    def exitStage(self, layer):
        """ Remove Layer from stage (No longer processing each frame) """
        if layer in self.stage:
            del self.stage[self.stage.index(layer)]

    def enterStage(self, layer):
        """ Add Layer to stage for processing next frame increment """
        self.stage.append(layer)



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