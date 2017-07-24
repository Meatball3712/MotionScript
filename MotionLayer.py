# Layer
from MotionLogger import buildDefaultLogger
from PIL import Image
import os

class Layer:
    """ A single layer or page in a motion object. Can have effects applied to it """

    def __init__(self, **kwargs):
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger()
        self.name = kwargs.get("name", "")
        self.type = kwargs.get("type", "image")
        self.path = kwargs.get("path", "")
        self.preload = kwargs.get("preload", True)
        self.position = kwargs.get("position", [0,0,0]) # X,Y,Z positions. (Z determines draw order)

        def copy(self, frame=self.frame):
            if self.
            return self.assets[frame].copy()

        def getNextImage(self):
            return self.asset


class ImageLayer(Layer):

    def __init__(self **kwargs):
        Layer.__init__(self, **kwargs)
        self.cycle = kwargs.get("cycle", True)
        self.asset.append(Image.open(self.path).convert("RGBA"))

    def _getAsset(self):
        return self.asset


class AnimationLayer(Layer):
    """ Animation Layer - Supports a cycle of images, path is a folder containing images """

    def __init__(self, **kwargs):
        Layer.__init__(self, **kwargs)
        self.extension = kwargs.get("extension", "") # Default to all files. Set to .png or similar to only pick those files.
        self.assets = []
        files = [x for x in os.listdir(self.path) if self.extension == "" or x[len(self.extension):] == self.extension]
        files.sort()
        for file in files:
            self.assets.append(Image.open(os.path.join(self.path, file)).convert("RGBA")) # Maybe make a way to get this on demand rather than leaving it in memory.
            
    def _getAsset(self):
        """ Retrieve current asset and increment frame """
        asset = self.assets[self.frame]
        self.frame = (self.frame + 1) % len(self.assets)
        return asset