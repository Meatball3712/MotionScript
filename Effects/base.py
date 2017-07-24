# Base Effect Superclass
from ..MotionLogger import buildDefaultLogger

class EffectConfigError(Exception):
    pass

class effect:
    """ Base Effect Class which will handle most initialisations """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.logger = kwargs["logger"] if kwargs.has_key("logger") else buildDefaultLogger().getChild("effect")
        if not kwargs.has_key("layer"):
            self.logger
        self.layer = kwargs["layer"]
