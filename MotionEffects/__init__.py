# Effects Module Init
import base
import translate
import fade

__all__ = ["base", "translate", "fade"]

effects = {
    "fadein":fade.FadeIn,
    "fadeout" : fade.FadeOut,
    "pan":translate.Pan,
    "zoom":translate.Zoom
}

def buildEffect(asset):
    effects.get(asset["subtype"], base.display)(**asset)
    return None