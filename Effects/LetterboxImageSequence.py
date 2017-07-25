import os
from PIL import Image

inpath = "A:\documents\RP\Savage Worlds\Sand and Sorrow\Animations\ComeLittleChildren_Courtyard\Sketchbook_Courtyard"
outpath = "A:\documents\RP\Savage Worlds\Sand and Sorrow\Animations\ComeLittleChildren_Courtyard\Python"

files = os.listdir(inpath)
files.sort()

for file in files:
    print "Processing %s" % file
    im = Image.open(os.path.join(inpath, file))
    im = im.crop((100,0,1820,1080))
    newIm = Image.new('RGBA',(1920,1080))
    newIm.paste(im, (100,0,1820,1080))
    newIm.save(os.path.join(outpath,file))
