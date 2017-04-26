from processing import *


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

export(bias_frame.createMaster(),"results/","masterbias")##testing

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
for i in range(len(red_lights)):
    red_lights_list.append(Light(Filter.RED,red_lights[i]))
    green_lights_list.append(Light(Filter.GREEN,green_lights[i]))
    blue_lights_list.append(Light(Filter.BLUE,blue_lights[i]))

##CREATING OFFSET VALUES FOR THE LIGHT FRAMES
originalx = 902
originaly = 611
          #Red,         #Green          #Blue
#offsets = [[[originalx,originaly],[900,609],[899,608]],  [[893,606],[892,607],[890,606]],     [[883,603],[882,602],[880,602]]]
offsets = [[[originalx,originaly],[893,606],[883,603]],  [[900,609],[892,607],[882,602]],     [[899,608],[890,606],[880,602]]]

##CREATING A STACK OF FRAMES
stack_rgb = RGBStack(bias_frame,dark_frame,red_flat_frame,green_flat_frame,blue_flat_frame,red_lights_list,green_lights_list,blue_lights_list,offsets,originalx,originaly)

##CALLING REDUCE FUNCTION ON THE FRAMES in a stack
stacks = stack_rgb.reduce()

##EXPORTING RGB IMAGE TO A FILE.
rgbfile = RGBFile()
rgbfile.overwrite("results/","cigargalaxy",stacks[0],stacks[1],stacks[2])
