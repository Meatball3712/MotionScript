# Effects Module Init
import base
import translate
import fade
import particles

__all__ = ["base", "translate", "fade"]

effects = {
    "fadein":fade.FadeIn,
    "fadeout" : fade.FadeOut,
    "pan":translate.Pan,
    "zoom":translate.Zoom,
    "display":base.Display,
    "particle" : particles.Emitter
}

def buildEffect(asset, logger):
    return effects.get(asset["subtype"], base.Display)(logger=logger, **asset)