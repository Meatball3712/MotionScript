import logging

def buildDefaultLogger(verbose=False, debug=False):
        """ Build Temporary Logger if one not supplied """
        logger = logging.getLogger("MotionScript")
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        if verbose or debug:
            ch.setLevel(logging.DEBUG)
        else:
            ch.setLevel(logging.INFO)
        logger.addHandler(ch)
        
        # debug
        if(debug or verbose):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        return logger