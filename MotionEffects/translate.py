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
        frame = self.asset.getNextFrame()
        if (self.duration) > 0:
            ef = self.getEasingFactor() if self.applyEasing else 1.0
            X = int(round(self.start_pos[0] + 1.0*((self.end_pos[0] - self.start_pos[0])/self.duration) * self.current * ef))
            Y = int(round(self.start_pos[1] + 1.0*((self.end_pos[1] - self.start_pos[1])/self.duration) * self.current * ef))
            self.logger.debug("%s Pan Calculations: X=%d, Y=%d, ef=%f, current=%d", self.name, X, Y, ef, self.current)
            newFrame = Image.new(size=self.size, mode="RGBA", color=(0,0,0,0))
            newFrame.paste(frame, (X,Y))
            frame = newFrame
        self.current = (self.current+1)%(self.duration+1) if self.loop and self.duration > 0 else self.current+1
        assert isinstance(frame, Image.Image), "frame is type %s" % type(frame)
        return frame
    
class Zoom(Effect):
    def __init__(self, **kwargs):
        Effect.__init__(self, effectName="Zoom", **kwargs)
        self.start_scale = kwargs.get("start_scale", 1.0)*1.0
        self.end_scale = kwargs.get("end_scale", 1.0)*1.0

    def getNextFrame(self):
        frame = self.asset.getNextFrame()
        self.current = (self.current+1)%(self.duration+1) if self.loop and self.duration > 0 else self.current+1
        ef = self.getEasingFactor() if self.applyEasing else 1.0
        scale = 1.0*self.start_scale + 1.0*((self.end_scale-self.start_scale)/self.duration)*self.current*ef
        width,height = frame.size
        width = int(round(width*scale))
        height = int(round(height*scale))
        X = int(round(self.position[0] - width/2.0)) # New Center X
        Y = int(round(self.position[1] - height/2.0))# New Center Y
        self.logger.debug("%s Zoom Calculations: position=%s, X=%d, Y=%d, Height=%d, Width=%d, ef=%f, current=%d", self.name, str(self.position), X, Y, width, height, ef, self.current)
        resized = frame.resize( (width, height) )
        newFrame = Image.new(size=self.size, mode="RGBA", color=(0,0,0,0))
        newFrame.paste(resized, (X,Y))
        frame = newFrame
        assert isinstance(frame, Image.Image), "frame is type %s" % type(frame)
        return frame