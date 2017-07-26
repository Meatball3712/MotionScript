# fade.py
from base import Effect
from PIL import Image
import numpy as np

def fadeImage(im, fadeFactor, size):
    arr = np.array(im) # Convert Image to Numpy Array
    alpha = arr[:,:,3].astype(float) # The alpha channel of all pixels currently in the image.
    alpha = np.rint(fadeFactor*alpha).astype(int) # Multiply by scaling factor and convert to ints.
    im.putalpha(alpha)
    Image.new(size=size, mode="RGBA", color = (0,0,0,0)).paste(im, (0,0))

class FadeIn(Effect):
    """ Fade in layer """
    def __init__(self, **kwargs):
        Effect.__init__(self, effectName="FadeIn", **kwargs)
        self.current_level = 0

    def getNextFrame(self):
        """ increase alpha over duration from 0x to 1x original """
        self.current_level = (1.0 * (self.current-self.start) / self.duration)
        im = self.asset.getNextFrame()
        return fadeImage(im, self.current_level, self.size)
        

class FadeOut(Effect):
    """ Fade out layer """
    def __init__(self, **kwargs):
        Effect.__init__(self, effectName="FadeIn", **kwargs)
        self.current_level = 1.0

    def getNextFrame(self):
        """ Decreases alpha over duration from 0x to 1x original """
        self.current_level = 1.0-(1.0 * (self.current-self.start) / self.duration)
        im = self.asset.getNextFrame()
        return fadeImage(im, self.current_level, self.size)