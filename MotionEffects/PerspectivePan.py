import os, math
from PIL import Image

bg_path = "A:\documents\RP\Savage Worlds\Sand and Sorrow\Animations\ComeLittleChildren_Courtyard\ComeLittleChildren_Moon.png"
mg_path = "A:\documents\RP\Savage Worlds\Sand and Sorrow\Animations\ComeLittleChildren_Courtyard\ComeLittleChildren_BG.png"
fg_path = "A:\documents\RP\Savage Worlds\Sand and Sorrow\Animations\ComeLittleChildren_Courtyard\ComeLittleChildren_FG.png"
output_path = "A:\documents\RP\Savage Worlds\Sand and Sorrow\Animations\ComeLittleChildren_Courtyard\Python"

fps = 24
duration = 4.00 # Seconds
stage = (1920,1007)

fg = Image.open(fg_path)
mg = Image.open(mg_path)
bg = Image.open(bg_path)

fg_X_start_offset   = -20
fg_X_end_offset     = 20
fg_Y_start_offset   = 0
fg_Y_end_offset     = 0

mg_X_start_offset   = -5
mg_X_end_offset     = 5
mg_Y_start_offset   = 0
mg_Y_end_offset     = 0

def getOffset(start,end,duration,time):
    offset = start + round( (end-start) * (time/duration) )
    return int(offset)

for frame in xrange(int(math.ceil(fps*duration))):
    print "Processing frame %04d" % frame
    fg_x_offset = getOffset(fg_X_start_offset, fg_X_end_offset, duration, frame/24.0)
    fg_y_offset = getOffset(fg_Y_start_offset, fg_Y_end_offset, duration, frame/24.0)
    mg_x_offset = getOffset(mg_X_start_offset, mg_X_end_offset, duration, frame/24.0)
    mg_y_offset = getOffset(mg_Y_start_offset, mg_Y_end_offset, duration, frame/24.0)

    print fg_x_offset, fg_y_offset
    print mg_x_offset, mg_y_offset

    newImage = Image.new('RGBA', stage)
    newImage.paste(bg.copy())
    
    new_mg = Image.new('RGBA', stage)
    new_mg.paste(mg.copy(), (mg_x_offset, mg_y_offset))
    newImage = Image.composite(new_mg, newImage, new_mg)

    new_fg = Image.new('RGBA', stage)
    new_fg.paste(fg.copy(), (fg_x_offset, fg_y_offset))
    newImage = Image.composite(new_fg, newImage, new_fg)

    filename = os.path.join(output_path, 'frame.%04d.png' % (frame+1))
    newImage.save(filename, "PNG")
