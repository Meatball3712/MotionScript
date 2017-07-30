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
    def __init__(self, config, eventConfig, logger):
        self.name = eventConfig["name"]
        self.start = eventConfig["start"]
        self.end = eventConfig["end"]
        self.position = eventConfig["position"]
        self.config = config
        self.logger = logger
        self.asset = self.buildAssets(eventConfig["asset"])
        
    def buildAssets(self, assetConfig):
        # Recursively build assets.
        if assetConfig["type"]  == "primative" and assetConfig["subtype"] == "image":
            assetConfig["size"]=assetConfig.get("size", self.config.size)
            self.logger.debug("Building Image Primative %s", assetConfig["name"])
            asset = MotionPrimative.MotionImage(logger=self.logger, **assetConfig)
        elif assetConfig["type"]  == "primative" and assetConfig["subtype"] == "animation":
            self.logger.debug("Building Image Animation %s", assetConfig["name"])
            asset = MotionPrimative.MotionAnimation(size=self.config.size, logger=self.logger, **assetConfig)
        else:
            self.logger.debug("Building %s Effect %s", assetConfig["subtype"], assetConfig["name"])
            assetConfig["size"]=assetConfig.get("size", self.config.size)
            assetConfig["start"] = assetConfig.get("start", self.start)
            assetConfig["end"] = assetConfig.get("end", self.end)
            assetConfig["asset"] = self.buildAssets(assetConfig["asset"])
            asset = MotionEffects.buildEffect(assetConfig, logger = self.logger)
        return asset

    def getNextFrame(self):
        return self.asset.getNextFrame()


class MotionScript:
    """Build Movie from assets and instructions"""
    def __init__(self, **kwargs):
        # Check valid config
        assert kwargs.has_key("config"), "config parameter not supplied"
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger(debug=kwargs.get("debug", False), verbose=kwargs.get("verbose", False))
        self.config = MotionScriptConfig(kwargs["config"], logger=self.logger)
        if not self.config.valid:
            raise InvalidMotionScript("Config invalid")
        else:
            self.logger.info("Config Validated")

        self.size = self.config.size
        self.duration = self.config.end-self.config.start
        self.events = {}
        self.timeline = {}
        self.stage = []
        self.logger.info("MotionScript initialised")
        self.logger.debug("Debugging messages enabled")
        self.build()
        self.animate()

    def build(self):
        self.logger.info("Building Movie...")
        # Build Timeline
        for event in self.config.story:
            # Build Assets
            e = MotionEvent(self.config, event, logger = self.logger)
            self.events[e.name] = e
            if not self.timeline.has_key(e.start):
                self.timeline[e.start] = []
            self.timeline[e.start].append(e.name)

            if not self.timeline.has_key(e.end):
                self.timeline[e.end] = []
            self.timeline[e.end].append(e.name)

        self.logger.debug("Time line created:\n%s", str(self.timeline))
        # Build Stage
        #self.updateStage()

        self.logger.info("Build Complete")

    def animate(self):
        self.logger.info("Animating...")
        for frame in xrange(self.duration):
            self.logger.info("\n\nComposing Frame %d/%d", frame, self.duration)
            screen = Image.new(size=self.size, mode="RGBA",color=(0,0,0,255))

            events = self.timeline.get(frame, []) # Get all new events for this moment, and process the stage.
            for event in events:
                e = self.events[event]
                self.logger.debug("Checking %s suitable for adding to stage: start=%d, end=%d", e.name, e.start, e.end)
                # Enter any new elements that are beginning
                if frame >= e.start and frame < e.end:
                    self.enterStage(event)

            # Build list of layers by sorted z_index
            layers = {}
            for event in self.stage:
                e = self.events[event]
                if not layers.has_key(e.position[2]):
                    layers[e.position[2]] = []
                layers[e.position[2]].append(e)

            ordered = layers.keys()
            ordered.sort()
            for index in ordered:
                for event in layers[index]:
                    im = event.getNextFrame()
                    assert isinstance(im, Image.Image), "Event Frame is type %s" % type(im)
                    screen = Image.alpha_composite(screen, im)
                    fname = os.path.join(self.config.output, "frame_%04d.png" % frame)
                    screen.save(fname, "PNG")

            # Remove finished events
            events = self.timeline.get(frame, []) # Get all new events for this moment, and process the stage.
            for event in events:
                e = self.events[event]
                self.logger.debug("Checking %s suitable for removing from stage: start=%d, end=%d, frame=%d", e.name, e.start, e.end, frame)
                # Exit any elements that have finished
                if frame >= e.end:
                    self.exitStage(event)
            
    def updateStage(self, frame=0):
        events = self.timeline.get(frame, []) # Get all new events for this moment, and process the stage.
        for event in events:
            # Exit any elements that have finished
            e = self.events[event]
            if e.end < frame:
                self.exitStage(event)
            # Enter any new elements that are beginning
            if e.start >= frame and e.end <= frame:
                self.enterStage(event)

    def exitStage(self, event):
        """ Remove Layer from stage (No longer processing each frame) """
        self.logger.debug("Removing %s from stage", event)
        if event in self.stage:
            del self.stage[self.stage.index(event)]

    def enterStage(self, event):
        """ Add Layer to stage for processing next frame increment """
        self.logger.debug("Adding %s to stage", event)
        self.stage.append(event)



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