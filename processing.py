from enum import Enum
import astropy
import math
import astropy
import numpy as np
from sklearn.preprocessing import normalize

from astropy.io import fits
##can be a collection of images, or a single master image.
##Can be a bias frame, dark frame flat frame or light frame
class Filter(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    LUMINESCANCE = 4
    NONE = 5

class Frame:
    def __init__(self):
        self.frames = []

    def getFrames(self):
        return self.frames

    def getExposure(self):
        ##assuming all exposures are equal time, for same filter same frame images.
        return float(self.frames[0].header["EXPOSURE"])

    def getTime(self):
        return self.frames[0].header["DATE-OBS"]

class Light(Frame):
    ##filter is Filter(Enum) frame is fits file opened
    def __init__(self,filter_,frame):
        Frame.__init__(self)
        self.filter = filter_
        self.frames.append(frame)

    def getFilter(self):
        return self.filter_

    def createMaster(self):
        return self.frames[0][0].data

class Bias(Frame):
    def __init__(self,frames):
        Frame.__init__(self)
        for frame in frames:
            self.frames.append(frame)

    def getNpArrays(self):
        return map(lambda x: x[0].data,self.frames)

    def createMaster(self):
        nparrays = self.getNpArrays()
        nparrayaverage = np.average(nparrays,axis=0)
        return nparrayaverage


class Dark(Frame):
    def __init__(self,frames):
        Frame.__init__(self)
        for frame in frames:
            self.frames.append(frame)

    def getNpArrays(self):
        return map(lambda x: x[0].data,self.frames)

    ##create basic ones that dont depend on bias?
    def createMaster(self,masterbias_np):
        ##numpy stuff to create master dark.
        nparrays = self.getNpArrays()
        nparrayaverage = np.average(nparrays,axis=0)

        masterdark_np = np.subtract(nparrayaverage,masterbias_np)
        return masterdark_np

    #perhaps support dependency injection by creating a fake generated dark master


class Flat(Frame):
    def __init__(self,frames,filter_):
        Frame.__init__(self)
        self.filter = filter_
        for frame in frames:
            self.frames.append(frame)

    def getFilter(self):
        return self.filter

    def getNpArrays(self):
        return map(lambda x: x[0].data,self.frames)

    def createMaster(self,masterbias_np,masterdark_np):
        print "creating flat master"
        nparrays = self.getNpArrays()
        masterflat_np = np.average(nparrays,axis=0)
        masterflat_np = np.subtract(masterflat_np,masterbias_np)
        masterflat_np = np.subtract(masterflat_np,masterdark_np)
        #got master flat.

        ##now normalize.
        masterflat_np = normalize(masterflat_np, axis=0)
        average = np.average(masterflat_np)
        ##bring back to resonable values
        masterflat_np = np.multiply(masterflat_np,1/average)
        return masterflat_np




class Stack:
    def __init__(self,masterbias,masterdark):
        self.masterbias = masterbias##single frame
        self.masterdark = masterdark##single frame


class RGBStack(Stack):
    def __init__(self,masterbias,masterdark,masterflatred,masterflatgreen,masterflatblue,redLights,greenLights,blueLights,offsets):
        Stack.__init__(self,masterbias,masterdark)
        self.masterflatred = masterflatred
        self.masterflatgreen = masterflatgreen
        self.masterflatblue = masterflatblue
        self.redLights = redLights
        self.greenLights = greenLights
        self.blueLights = blueLights
        self.offsets = offsets


    def reduce(self):
        ##TODO:ensure the exposure time is equal where it matters.
        ##TODO:ensure the filters line up.

        ##Bias substraction
        masterbias_np = self.masterbias.createMaster()
        ##Dark substraction
        masterdark_np = self.masterdark.createMaster(masterbias_np)

        ##Flat Division
        masterflatred_np = self.masterflatred.createMaster(masterbias_np,masterdark_np)

        masterflatgreen_np = self.masterflatgreen.createMaster(masterbias_np,masterdark_np)

        masterflatblue_np = self.masterflatblue.createMaster(masterbias_np,masterdark_np)


        ##single frame reduction(RED)
        masterreds = []
        for redlightframe in self.redLights:
            master_redlight_np = redlightframe.createMaster()##gets the one frame

            master_redlight_np = np.subtract(master_redlight_np,masterbias_np)
            master_redlight_np = np.substract(master_redlight_np,masterdark_np)
            master_redlight_np = np.divide(master_redlight_np,masterflatred_np)
            masterreds.append(master_redlight_np)

        ##single frame reduction (GREEN)
        mastergreens = []
        for greenlightframe in self.greenLights:
            master_greenlight_np = redlightframe.createMaster()##gets the one frame

            master_greenlight_np = np.subtract(master_greenlight_np,masterbias_np)
            master_greenlight_np = np.substract(master_greenlight_np,masterdark_np)
            master_greenlight_np = np.divide(master_greenlight_np,masterflatgreen_np)
            mastergreens.append(master_greenlight_np)

        ##single frame reduction (BLUE)
        masterblues = []
        for bluelightframe in self.blueLights:
            master_bluelight_np = redlightframe.createMaster()##gets the one frame

            master_bluelight_np = np.subtract(master_bluelight_np,masterbias_np)
            master_bluelight_np = np.substract(master_bluelight_np,masterdark_np)
            master_bluelight_np = np.divide(master_bluelight_np,masterflatblue_np)
            masterblues.append(master_bluelight_np)

        ##OFFSETTING
        masteroffsetredframes = []
        masteroffsetgreenframes = []
        masteroffsetblueframes = []

        #for masterredframe_np in masterreds:
            #offset(masterredframe_np,offsetred[i])
        #for mastergreenframe_np in mastergreens:
            #offset(masterredframe_np,offsetgreen[i])
        #for masterblueframe_np in masterblues:
            #offset(masterredframe_np,offsetblue[i])

        masteroffsetredframes = masterreds
        masteroffsetgreenframes = mastergreens
        masteroffsetblueframes = masterblues




        ##stacking
        ##cosmic rays removal.
        pass





#IMPORTING
source = '../../../dropbox/astrohirsch/FridayNight/'
red = fits.open(source+'RingNEBULA-0132.fit')
print red[0].header

biases = [fits.open(source+'RingNEBULA-0144.fit'),fits.open(source+'RingNEBULA-0154.fit')]
darks = [fits.open(source+'RingNEBULA-009Dark5.fit'),fits.open(source+'RingNEBULA-010Dark5.fit')]
redflats = [fits.open(source+'RingNEBULA-029amazingFR.fit'),fits.open(source+'RingNEBULA-030amazingFR.fit')]
greenflats = [fits.open(source+'RingNEBULA-029amazingFG.fit'),fits.open(source+'RingNEBULA-030amazingFG.fit')]
blueflats = [fits.open(source+'RingNEBULA-029amazingFB.fit'),fits.open(source+'RingNEBULA-030amazingFB.fit')]

red_lights = [fits.open(source+'RingNEBULA-0091.fit'),fits.open(source+'RingNEBULA-0101.fit')]
green_lights = [fits.open(source+'RingNEBULA-0092.fit'),fits.open(source+'RingNEBULA-0102.fit')]
blue_lights = [fits.open(source+'RingNEBULA-0093.fit'),fits.open(source+'RingNEBULA-0103.fit')]

bias_frame = Bias(biases)
#masterbias = bias.createMaster()
dark_frame = Dark(darks)
#dark_frame.createMaster(masterbias)
red_flat_frame = Flat(redflats,Filter.RED)
green_flat_frame = Flat(greenflats,Filter.GREEN)
blue_flat_frame = Flat(blueflats,Filter.BLUE)
red_lights = []
green_lights = []
blue_lights = []
for i in range(len(red_lights)):
    red_lights.append(Light(red_lights[i],Filter.RED))
    green_lights.append(Light(green_lights[i],Filter.GREEN))
    blue_lights.append(Light(blue_lights[i],Filter.BLUE))

stack_rgb = RGBStack(bias_frame,dark_frame,red_flat_frame,green_flat_frame,blue_flat_frame,red_lights,green_lights,blue_lights,[])
stack_rgb.reduce()
