# Layer
from MotionLogger import buildDefaultLogger
from PIL import Image
import os

class MotionPrimative:
    """ A single layer or page in a motion object. Can have effects applied to it """

    def __init__(self, **kwargs):
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger()
        self.name = kwargs.get("name", "")
        self.type = kwargs.get("type", "image")
        self.path = kwargs.get("path", "")
        self.size = kwargs.get("size", None)
        self.preload = kwargs.get("preload", True)
        self.position = kwargs.get("position", [0,0,0]) # X,Y,Z positions. (Z determines draw order)
        self.size = kwargs["size"]
        self.assets = []
        self.current = 0

        def copy(self, frame=self.current):
            return self.assets[frame%len(self.assets)].copy()

        def getNextFrame(self):
            self.current += 1
            return self.assets[0].copy()

class MotionImage(MotionPrimative):
    """ A static Image """
    def __init__(self, **kwargs):
        MotionPrimative.__init__(self, **kwargs)
        self.cycle = kwargs.get("cycle", True)
        asset_im = Image.open(self.path).convert("RGBA")
        if self.size and asset_im.size != self.size:
            asset_im = asset_im.resize(self.size)
        self.assets.append(asset_im)
        self.logger.debug("Image Primative %s initialised", self.name)

    def getNextFrame(self):
        self.logger.debug("Retrieving Frame %d from %s", self.current, self.name)
        asset = self.assets[0].copy()
        assert isinstance(asset, Image.Image), "asset is type %s" % type(asset)
        return asset


class MotionAnimation(MotionPrimative):
    """ Animation MotionPrimative - Supports a cycle of images, path is a folder containing images """

    def __init__(self, **kwargs):
        MotionPrimative.__init__(self, **kwargs)
        self.extension = kwargs.get("extension", "") # Default to all files. Set to .png or similar to only pick those files.
        self.assets = []
        files = [x for x in os.listdir(self.path) if self.extension == "" or x[len(self.extension):] == self.extension]
        files.sort()
        for file in files:
            asset_im = Image.open(os.path.join(self.path, file)).convert("RGBA")
            if self.size and self.size != asset_im.size:
                asset_im = asset_im.resize(self.size)
            self.assets.append() # Maybe make a way to get this on demand rather than leaving it in memory.
        self.logger.debug("Animation Primative %s initialised", self.name)
            
    def getNextFrame(self):
        """ Retrieve current asset and increment frame """
        self.logger.debug("Retrieving Frame %d from %s", self.current, self.name)
        asset = self.assets[self.current]
        self.current = (self.current + 1) % len(self.assets)
        assert isinstance(asset, Image.Image), "asset is type %s" % type(asset)
        return asset