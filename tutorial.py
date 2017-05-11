from processing import *
from highprocessing import *
from astrophysics import *
#IMPORTING

source = '/Users/luciencd/downloads/PURE_HIRSCH_DATA/'

source2 = '/Users/luciencd/dropbox/astrohirsch/FridayNight/'


##BIASES
biases = map(lambda t:fits.open(source+'Bias-'+str(str(t).zfill(3))+'Bias.fit'),range(1,31))#0,30 inclusive

##DARKS
darks = map(lambda t:fits.open(source2+'RingNEBULA-'+str(str(t).zfill(3))+'Dark5.fit'),range(9,14))

##FLATS
redflats = map(lambda t:fits.open(source+'Flat-'+str(str(t).zfill(3))+'Red.fit'),range(1,6))
greenflats = map(lambda t:fits.open(source+'Flat-'+str(str(t).zfill(3))+'Green.fit'),range(1,6))
blueflats = map(lambda t:fits.open(source+'Flat-'+str(str(t).zfill(3))+'Blue.fit'),range(1,6))

#LIGHTS
red_lights = map(lambda t:fits.open(source+'m13-'+str(str(t).zfill(3))+'Red.fit'),range(1,6))
green_lights = map(lambda t:fits.open(source+'m13-'+str(str(t).zfill(3))+'Green.fit'),range(1,6))
blue_lights = map(lambda t:fits.open(source+'m13-'+str(str(t).zfill(3))+'Blue.fit'),range(1,6))

##CREATING FRAMES
##CREATING BIAS FRAME
bias_frame = Bias(biases)

##CREATING DARK FRAME
dark_frame = Dark(darks)##there were problems with binning, so the resolution isn't the same.
dark_frame.width = bias_frame.getWidth()
dark_frame.height = bias_frame.getHeight()

#dark_frame.createMaster(masterbias)

##CREATING FLAT FRAMES
red_flat_frame = Flat(Filter.RED,redflats)
green_flat_frame = Flat(Filter.GREEN,greenflats)
blue_flat_frame = Flat(Filter.BLUE,blueflats)

##CREATING OFFSET VALUES FOR THE LIGHT FRAMES
originalx = 532
originaly = 713

offsets = [[[originalx,originaly],  [511,709],[498,707],[482,704],[464,702]],\
            [[522,711],             [508,709],[493,706],[474,702],[457,700]],\
            [[522,714],             [503,708],[488,705],[470,703],[448,699]]]

##CREATING LIGHT FRAMES
red_lights_list = []
green_lights_list = []
blue_lights_list = []
for i in range(len(red_lights)):
    red_lights_list.append(Light(Filter.RED,red_lights[i]))
    green_lights_list.append(Light(Filter.GREEN,green_lights[i]))
    blue_lights_list.append(Light(Filter.BLUE,blue_lights[i]))

for i in range(len(red_lights)):
    red_lights_list[i].trackingStar(offsets[0][i][0],offsets[0][i][1])
    green_lights_list[i].trackingStar(offsets[1][i][0],offsets[1][i][1])
    blue_lights_list[i].trackingStar(offsets[2][i][0],offsets[2][i][1])


red_lights_list = red_lights_list[1:3]
green_lights_list = green_lights_list[0:3]
blue_lights_list = blue_lights_list[1:3]



##Use machine learning to use the time delta, filter => x, y to interpolate using regression over the non-corrected ones.

##CREATING A STACK OF FRAMES
stack_rgb = RGBStack(bias_frame,dark_frame,red_flat_frame,green_flat_frame,blue_flat_frame,red_lights_list,green_lights_list,blue_lights_list)

##CALLING REDUCE FUNCTION ON THE FRAMES in a stack
stack_rgb.reduceAutomatic()

##CALCULATE OFFSET AND REASSIGN star position on all the reducedFrames.
reducedReds = stack_rgb.reducedReds
reducedGreens = stack_rgb.reducedGreens
reducedBlues = stack_rgb.reducedBlues

##CALLING STACK FUNCTION ON THE FRAMES in a stack
stack_rgb.stackAutomatic()

##EXTRACTING ALL THE np arrays and FRAMES
masterbias_np = stack_rgb.masterbias_np #master nparray
masterdark_np = stack_rgb.masterdark_np #master nparray

masterflatred_np = stack_rgb.masterflatred_np #master nparray
masterflatgreen_np = stack_rgb.masterflatgreen_np #master nparray
masterflatblue_np = stack_rgb.masterflatblue_np #master nparray

redstack = stack_rgb.stackedRedFrame #StackedFrame
greenstack = stack_rgb.stackedGreenFrame #StackedFrame
bluestack = stack_rgb.stackedBlueFrame #StackedFrame


##EXPORTING RGB IMAGE TO A FILE.
rgbfile = RGBFile()  #folderpath, filename,StackedFrame,StackedFrame,StackedFrame
rgbfile.overwrite("results/example/","m13example",redstack,greenstack,bluestack)

export("results/example/","bias",masterbias_np)
export("results/example/","dark",masterdark_np)
export("results/example/","flatred",masterflatred_np)
export("results/example/","flatgreen",masterflatgreen_np)
export("results/example/","flatblue",masterflatblue_np)
