# Test Run
import os, sys, inspect
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
sys.path.insert(0,parentDir)
import MotionScript
debug = False
MS = MotionScript.MotionScript(verbose=debug, debug=debug, config="MagnetTest.json")