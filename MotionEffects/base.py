# Base Effect Superclass
import os, sys, inspect
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
sys.path.insert(0,parentDir)
from MotionLogger import buildDefaultLogger
from MotionPrimative import MotionPrimative


from PIL import Image

class EffectConfigError(Exception):
    pass

class Effect:
    """ Base Effect Class which will handle most initialisations """

    def __init__(self, asset, size, name, **kwargs):
        self.asset = asset
        self.size = size
        self.name = name
        self.effectName = kwargs.get("effectName", "base")
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger().getChild("effect_%s" % self.effectName)

        # Timing - Requires start and duration or start and end.
        self.start = kwargs.get("start", 0)
        self.end = kwargs.get("end", 0)
        self.duration = kwargs.get("duration", (self.end - self.start))
        self.end = self.end if self.end > self.start else self.start + self.duration
        self.current = self.start

        # Default Ease in and Ease out.
        self.applyEasing = kwargs.get("applyEasing", False)
        self.easing_p0 = 0
        self.easing_p1 = 0
        self.easing_p2 = 1
        self.easing_p3 = 1

        # Validation
        assert self.duration > 0, "Invalid duration for Effect %s" % self.name
        assert self.end > self.start, "Invalid start/end for Effect %s" % self.name
        assert isinstance(self.asset, MotionPrimative) or isinstance(self.asset, Effect), "Provided asset is not a valid Effect or MotionPrimative Object in Effect %s" % self.name


    def getEasingFactor(self, **kwargs):
        """ Using supplied parameters, and current place in between start/end, determine the easing factor (Bezier). 
        To be multiplied by the current frame to determine the relative frame to pretend to be on """
        if self.duration > 0:
            p0 = kwargs.get("p0", self.easing_p0)
            p1 = kwargs.get("p1", self.easing_p1)
            p2 = kwargs.get("p2", self.easing_p2)
            p3 = kwargs.get("p3", self.easing_p3)
            t = kwargs.get("t", (1.0*self.current / self.duration))

            # B(t) = (1-t)^3 * p0 + 3(1-t)^2*t*p1 + 3(1-t)*t^2*p2 + t^3*p3
            ef = (1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3
        else:
            ef = 1

        # 0 <= ef <= 1
        return ef

    def getNextFrame(self):
        """ The Base Effect simply returns the next image in the sequence on the correct canvas size """
        self.current = (self.current+1)%self.duration if self.loop else self.current+1
        return Image.new(self.size, "RGBA").paste(self.asset.getNextFrame())


class display(Effect):
    """ Just show the image in place - no modifications """

    def __init__(self, asset, size, name, **kwargs):
        Effect.__init__(self, asset=asset, size=size, name=name, effectName="display", **kwargs)


