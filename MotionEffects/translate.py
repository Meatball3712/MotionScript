# Translate
from base import Effect
from PIL import Image

class Pan(Effect):
    """Move an image around the screen"""
    def __init__(self, **kwargs):
        Effect.__init__(self, effectName="Pan", **kwargs)
        self.start_pos = kwargs.get("start_pos", [0,0])
        self.end_pos = kwargs.get("end_pos", [0,0])
        self.current_pos = self.start_pos

    def getNextFrame(self):
        im = self.asset.getNextImage()
        if (self.duration) > 0:
            ef = self.getEasingFactor() if self.applyEasing else 1.0
            X = int(round(1.0*(self.end_pos[0] - self.start_pos[0])/(self.end-self.start) * self.current * ef))
            Y = int(round(1.0*(self.end_pos[1] - self.start_pos[1])/(self.end-self.start) * self.current * ef))
            im = Image.new(self.size, "RGBA").paste(im, (X,Y))
        self.current = (self.current+1)%(self.end-self.start) if self.loop and (self.end-self.start) > 0 else self.current+1
        return im


    
class Zoom(Effect):
    def __init__(self, **kwargs):
        Effect.__init__(self, effectName="Zoom", **kwargs)
        self.start_scale = kwargs.get("start_scale", 1.0)
        self.end_scale = kwargs.get("end_scale", 1.0)

    def getNextFrame(self):
        self.current = (self.current+1)%(self.end-self.start) if self.loop and (self.end-self.start) > 0 else self.current+1
        return self.asset.getNextImage()