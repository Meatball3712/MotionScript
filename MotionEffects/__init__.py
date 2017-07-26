# Effects Module Init
import base
import translate
import fade

__all__ = ["base", "translate", "fade"]

effects = {
    "fadein":fade.FadeIn,
    "fadeout" : fade.FadeOut,
    "pan":translate.Pan,
    "zoom":translate.Zoom,
    "display":base.Display
}

def buildEffect(asset, logger):
    return effects.get(asset["subtype"], base.Display)(logger=logger, **asset)