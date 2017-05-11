from library.processing import *


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
red_lights = map(lambda t:fits.open(source+'m82-'+str(str(t).zfill(3))+'Red.fit'),range(1,4))
green_lights = map(lambda t:fits.open(source+'m82-'+str(str(t).zfill(3))+'Green.fit'),range(1,4))
blue_lights = map(lambda t:fits.open(source+'m82-'+str(str(t).zfill(3))+'Blue.fit'),range(1,4))


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

##CREATING LIGHT FRAMES
red_lights_list = []
green_lights_list = []
blue_lights_list = []

##CREATING OFFSET VALUES FOR THE LIGHT FRAMES
originalx = 902
originaly = 611
          #Red,         #Green          #Blue
#offsets = [[[originalx,originaly],[900,609],[899,608]],  [[893,606],[892,607],[890,606]],     [[883,603],[882,602],[880,602]]]
offsets = [[[originalx,originaly],[893,606],[883,603]],  [[900,609],[892,607],[882,602]],     [[899,608],[890,606],[880,602]]]

for i in range(len(red_lights)):
    red_frame = Light(Filter.RED,red_lights[i])
    red_frame.trackingStar(offsets[0][i][0],offsets[0][i][1])
    red_lights_list.append(red_frame)
    green_frame = Light(Filter.GREEN,green_lights[i])
    green_frame.trackingStar(offsets[0][i][0],offsets[0][i][1])
    green_lights_list.append(green_frame)
    blue_frame = Light(Filter.BLUE,blue_lights[i])
    blue_frame.trackingStar(offsets[0][i][0],offsets[0][i][1])
    blue_lights_list.append(blue_frame)




##CREATING A STACK OF FRAMES
stack_rgb = RGBStacker(bias_frame,dark_frame,red_flat_frame,green_flat_frame,blue_flat_frame,red_lights_list,green_lights_list,blue_lights_list)

##CALLING REDUCE FUNCTION ON THE FRAMES in a stack
stack_rgb.reduceAutomatic()

##CALCULATE OFFSET AND REASSIGN star position on all the reducedFrames.

##TODO: Use machine learning to use the time delta, filter => x, y to interpolate using regression over the non-corrected ones.
##TODO: Calculate the center of mass of center quarter of image, and use that as standard star.
##TODO: do star centroid analysis, id them, then rank them by counts, and pair up the most remote count values to track it.
##Assuming that after reduction, all frames are the same length, and approximately have the same number of counts.

reducedReds = stack_rgb.reducedReds
reducedGreens = stack_rgb.reducedGreens
reducedBlues = stack_rgb.reducedBlues

##TODO: could remove shitty frames here.


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
rgbfile.overwrite("results/example/cigargalaxy/","cigargalaxy",redstack.createMaster(),greenstack.createMaster(),bluestack.createMaster())
