from enum import Enum
import astropy
import math
import astropy
import numpy as np
from sklearn.preprocessing import normalize
import os
from astropy.io import fits
import copy
def binArray(data, axis, binstep, binsize, func=np.nanmean):
    data = np.array(data)
    dims = np.array(data.shape)
    argdims = np.arange(data.ndim)
    argdims[0], argdims[axis]= argdims[axis], argdims[0]
    data = data.transpose(argdims)
    data = [func(np.take(data,np.arange(int(i*binstep),int(i*binstep+binsize)),0),0) for i in np.arange(dims[axis]//binstep)]
    data = np.array(data).transpose(argdims)
    return data

def export(data,zipdest,target):
    ##TODO: remove file directory dependency
    try:
        os.remove(zipdest+target+'.fit')
    except OSError:
        pass

    example = "fitses/examplefitsR.fit"
    fixedr = fits.open(example)
    data_next = fits.PrimaryHDU(data)
    fixedRfile = fits.HDUList([data_next])
    fixedRfile.writeto(zipdest+target+".fit")

class RGBFile:
    def __init__(self,filesource="."):
        self.filesource = filesource
        self.redexample = "fitses/examplefitsR.fit"
        self.greenexample = "fitses/examplefitsG.fit"
        self.blueexample = "fitses/examplefitsB.fit"

    def save(self,zipdest,target,redfinalstack_np,greenfinalstack_np,bluefinalstack_np):
        redfilename = zipdest+target+'redfinal.fit'
        greenfilename = zipdest+target+'greenfinal.fit'
        bluefilename = zipdest+target+'bluefinal.fit'

        fixedr = fits.open(self.redexample)
        fixedg = fits.open(self.greenexample)
        fixedb = fits.open(self.blueexample)

        rafterflatdata = fits.PrimaryHDU(redfinalstack_np)
        fixedRfile = fits.HDUList([rafterflatdata])
        fixedRfile.writeto(redfilename)

        gafterflatdata = fits.PrimaryHDU(greenfinalstack_np)
        fixedGfile = fits.HDUList([gafterflatdata])
        fixedGfile.writeto(greenfilename)

        bafterflatdata = fits.PrimaryHDU(bluefinalstack_np)
        fixedBfile = fits.HDUList([bafterflatdata])
        fixedBfile.writeto(bluefilename)



    def overwrite(self,zipdest,target,redfinalstack_np,greenfinalstack_np,bluefinalstack_np):
        #removing files that were there before.
        try:
            os.remove(zipdest+target+'redfinal.fit')
            os.remove(zipdest+target+'greenfinal.fit')
            os.remove(zipdest+target+'bluefinal.fit')
        except OSError:
            pass

        self.save(zipdest,target,redfinalstack_np,greenfinalstack_np,bluefinalstack_np)
'''
class MonoFile:
    def __init__(self,filesource="."):
        self.filesource
    def save(self,zipdest,target,finalstack_np):
        redfilename = zipdest+target+'redfinal.fit'
'''

##can be a collection of images, or a single master image.
##Can be a bias frame, dark frame flat frame or light frame
class Filter(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    LUMINESCANCE = 4
    NONE = 5

##truly should be an interface
class Frame:
    def __init__(self):
        self.frames = []

    def getFrames(self):
        return self.frames

    def getExposure(self):
        ##assuming all exposures are equal time, for same filter same frame images.
        return float(self.frames[0][0].header["EXPOSURE"])

    def getTime(self):
        return self.frames[0].header["DATE-OBS"]

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

class Light(Frame):
    ##filter is Filter(Enum) frame is fits file opened
    def __init__(self,filter_,frame):
        Frame.__init__(self)
        self.filter = filter_
        self.frames.append(frame)
        self.width = self.frames[0][0].header["NAXIS1"]
        self.height = self.frames[0][0].header["NAXIS2"]
        self.starx = self.width/2
        self.stary = self.height/2
        self.corrected = False

    def getFilter(self):
        return self.filter_

    def createMaster(self):
        return np.array(self.frames[0][0].data)

    def trackingStar(self,x,y):
        self.starx = x
        self.stary = y
        self.corrected = True

    def getStarx(self):
        return self.starx

    def getStary(self):
        return self.stary

class Bias(Frame):
    def __init__(self,frames):
        Frame.__init__(self)
        for frame in frames:
            self.frames.append(frame)

        self.width = self.frames[0][0].header["NAXIS1"]
        self.height = self.frames[0][0].header["NAXIS2"]

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
        self.width = self.frames[0][0].header["NAXIS1"]
        self.height = self.frames[0][0].header["NAXIS2"]

    def getNpArrays(self):
        return map(lambda x: x[0].data,self.frames)

    ##create basic ones that dont depend on bias?
    def createMaster(self,masterbias_np,multiplier):
        ##numpy stuff to create master dark.
        nparrays = self.getNpArrays()
        nparrayaverage = np.average(nparrays,axis=0)


        masterdark_np = np.subtract(nparrayaverage,masterbias_np)
        masterdark_np = np.divide(masterdark_np,multiplier)
        return masterdark_np

    def getGeneric(self):
        return np.zeros((self.getHeight(), self.getWidth()))

    #perhaps support dependency injection by creating a fake generated dark master


class Flat(Frame):
    def __init__(self,filter_,frames):
        Frame.__init__(self)
        self.filter = filter_
        for frame in frames:
            self.frames.append(frame)

        self.width = self.frames[0][0].header["NAXIS1"]
        self.height = self.frames[0][0].header["NAXIS2"]

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


class ReducedFrame(Frame):#reducedframe self input is a light frame.
    def __init__(self,reduced_np,lightframe):
        Frame.__init__(self)
        self.frame = lightframe
        self.reduced_np = reduced_np

    def getFilter(self):
        return self.lightframe.filter_

    def createMaster(self):
        return self.reduced_np

    def trackingStar(self,x,y):
        lightframe.trackingStar(x,y)

    def getStarx(self):
        lightframe.getStarx()

    def getStary(self):
        lightframe.getStary()

class StackedFrame(Frame):#reducedframe self input is a light frame.
    def __init__(self,reduced_np,lightframe):
        Frame.__init__(self)
        self.frame = lightframe
        self.reduced_np = reduced_np

    def getFilter(self):
        return self.lightframe.filter_

    def createMaster(self):
        return self.reduced_np

    def trackingStar(self,x,y):
        lightframe.trackingStar(x,y)

    def getStarx(self):
        lightframe.getStarx()

    def getStary(self):
        lightframe.getStary()

class Stacker:
    def __init__(self,masterbias,masterdark):
        self.masterbias = masterbias##single frame
        self.masterdark = masterdark##single frame


class RGBStacker(Stack):
    def __init__(self,masterbias,masterdark,masterflatred,masterflatgreen,masterflatblue,redLights,greenLights,blueLights):
        Stack.__init__(self,masterbias,masterdark)
        self.masterflatred = masterflatred
        self.masterflatgreen = masterflatgreen
        self.masterflatblue = masterflatblue
        self.redLights = redLights
        self.greenLights = greenLights
        self.blueLights = blueLights

    def offset(self,frame,x1,y1,x2,y2):
        offsetframe = copy.deepcopy(frame)
        #print range((y1-y2),len(frame)+(y1-y2))

        width = frame.shape[0]
        height = frame.shape[1]
        for row in range(0,width-int(math.fabs(y1-y2))):
            #print len(frame[row]),(x1-x2)
            for cell in range(0,height-int(math.fabs(x1-x2))):
                offsetframe[row][cell] = frame[row+(y1-y2)][cell+(x1-x2)]

        return offsetframe


    def generateMasters(self):
        ##Bias substraction
        self.masterbias_np = self.masterbias.createMaster()
        ##Dark substraction
        #masterdark_np = self.masterdark.createMaster(masterbias_np)
        self.masterdark_np = self.masterdark.createMaster(masterbias_np,self.masterdark.getExposure()/self.redLights[0].getExposure())##GENERIC DARK FRAME!!! because of binning, impossible to combine the two

        #export(masterdark_np,"results/","masterdark")
        ##Flat Division #red is 5 seconds, dark is 30 seconds.

        self.masterflatred_np = self.masterflatred.createMaster(masterbias_np,np.multiply(masterdark_np,self.masterflatred.getExposure()/self.masterdark.getExposure()))
        #print "dark red differences:",np.multiply(masterdark_np,self.masterflatred.getExposure()/self.masterdark.getExposure())
        self.masterflatgreen_np = self.masterflatgreen.createMaster(masterbias_np,np.multiply(masterdark_np,self.masterflatgreen.getExposure()/self.masterdark.getExposure()))
        #print "dark green differences:",np.multiply(masterdark_np,self.masterflatgreen.getExposure()/self.masterdark.getExposure())
        self.masterflatblue_np = self.masterflatblue.createMaster(masterbias_np,np.multiply(masterdark_np,self.masterflatblue.getExposure()/self.masterdark.getExposure()))

    ##takes in bias, dark and flat Numpy arrays, and single light(Frame) object, and returns ReducedFrame(Frame)
    def reduceFrame(self,masterbias_np,masterdark_np,masterflat_np,lightframe):
        masterlight_np = redlightframe.createMaster()##gets the one frame
        #print "before bias removal",master_redlight_np
        masterlight_np = np.subtract(masterlight_np,masterbias_np)
        #print "after bias removal",master_redlight_np
        masterlight_np = np.subtract(masterlight_np,masterdark_np)
        masterlight_np = np.divide(masterlight_np,masterflat_np)

        reduced_frame = ReducedFrame(masterlight_np,lightframe)
        return reduced_frame

    ##takes list of bias, dark and flat Numpy arrays, and single light(Frame) object, and returns ReducedFrame(Frame)
    def reduceAllFrames(self,masterbias_np,masterdark_np,masterflat_np,lightframes):
        ##TODO:ensure the exposure time is equal where it matters.
        ##TODO:ensure the filters line up.
        return map(lambda f: reduceFrame(masterbias_np,masterdark_np,masterflat_np,f),lightframes)

    def reduce(self,masterbias_np,masterdark_np,masterflatred_np,masterflatgreen_np,masterflatblue_np,redLights,greenLights,blueLights):

        ##single frame reduction(RED)
        reduced_light_reds = []
        for redlightframe in redLights:
            master_redlight_np = redlightframe.createMaster()##gets the one frame

            #TODO:dark corrections for exposure time of flat frame!
            #print "before bias removal",master_redlight_np
            master_redlight_np = np.subtract(master_redlight_np,masterbias_np)
            #print "after bias removal",master_redlight_np
            master_redlight_np = np.subtract(master_redlight_np,masterdark_np)
            master_redlight_np = np.divide(master_redlight_np,masterflatred_np)

            reduced_red = ReducedFrame(master_redlight_np,redlightframe)
            reduced_light_reds.append(reduced_red)

        ##single frame reduction (GREEN)
        reduced_light_greens = []
        for greenlightframe in greenLights:
            master_greenlight_np = greenlightframe.createMaster()##gets the one frame

            master_greenlight_np = np.subtract(master_greenlight_np,masterbias_np)
            master_greenlight_np = np.subtract(master_greenlight_np,masterdark_np)
            master_greenlight_np = np.divide(master_greenlight_np,masterflatgreen_np)

            reduced_green = ReducedFrame(master_greenlight_np,greenlightframe)
            mastergreens.append(master_greenlight_np)

        ##single frame reduction (BLUE)
        reduced_light_blues = []
        for bluelightframe in blueLights:
            master_bluelight_np = bluelightframe.createMaster()##gets the one frame

            master_bluelight_np = np.subtract(master_bluelight_np,masterbias_np)
            master_bluelight_np = np.subtract(master_bluelight_np,masterdark_np)
            master_bluelight_np = np.divide(master_bluelight_np,masterflatblue_np)

            reduced_blues = ReducedFrame(master_bluelight_np,bluelightframe)
            reduced_light_blues.append(master_bluelight_np)


        self.reduced_light_reds = reduced_light_reds
        self.reduced_light_greens = reduced_light_greens
        self.reduced_light_blues = reduced_light_blues

    def stackColor(self,reduced_lights):
        masteroffset_list = []

        for i in range(len(reduced_lights)):
            masterframe = reduced_lights[i]
            originalframe = reduced_lights[0]
            masterframe_np = masterframe.createMaster()
            masteroffset_list.append(self.offset(masterframe_np,masterframe.getStarx(),masterframe.getStary(),originalframe.getStarx(),originalframe.getStary()))

        masteroffset_np = np.average(masteroffset_list,axis=0)
        return map(lambda y: map(lambda x: max(0.0,x),y),masteroffset_np)


    def stack(self,reduced_light_reds,reduced_light_greens,reduced_light_blues):
        ##TODO:Pass in an averaging function? for large light frames do median, but small ones do average?

        ##OFFSETTING
        masteroffsetred_list = []
        masteroffsetgreen_list = []
        masteroffsetblue_list = []

        for i in range(len(reduced_light_reds)):
            masterredframe = reduced_light_reds[i]
            originalredframe = reduced_light_reds[0]
            masterredframe_np = masterredframe.createMaster()
            masteroffsetred_list.append(self.offset(masterredframe_np,masterredframe.getStarx(),masterredframe.getStary(),originalredframe.getStarx(),originalredframe.getStary()))

        for i in range(len(reduced_light_greens)):
            mastergreenframe = reduced_light_greens[i]
            originalgreenframe = reduced_light_greens[0]
            mastergreenframe_np = mastergreenframe.createMaster()
            masteroffsetgreen_list.append(self.offset(mastergreenframe_np,mastergreenframe.getStarx(),mastergreenframe.getStary(),originalgreenframe.getStarx(),originalgreenframe.getStary()))

        for i in range(len(reduced_light_blues)):
            masterblueframe = reduced_light_blues[i]
            originalblueframe = reduced_light_blues[0]
            masterblueframe_np = masterblueframe.createMaster()
            masteroffsetblue_list.append(self.offset(masterblueframe_np,masterblueframe.getStarx(),masterblueframe.getStary(),originalblueframe.getStarx(),originalblueframe.getStary()))

        masteroffsetred_np = np.average(masteroffsetred_list,axis=0)
        masteroffsetgreen_np = np.average(masteroffsetgreen_list,axis=0)
        masteroffsetblue_np = np.average(masteroffsetblue_list,axis=0)
        ##can use median for getting rid of cosmic rays, if you have a lot of light frames.


        map(lambda y: map(lambda x: max(0.0,x),y),masteroffsetred_np)
        map(lambda y: map(lambda x: max(0.0,x),y),masteroffsetgreen_np)
        map(lambda y: map(lambda x: max(0.0,x),y),masteroffsetblue_np)

        self.stacked_light_red = masterreds
        self.stacked_light_green = mastergreens
        self.stacked_light_blue = masterblues

    #requires stackAutomatic to be run.
    def getFinal(self):
        pass
    def reduceAutomatic(self):
        ##generateMasters
        self.generateMasters()

        ##reduce red light frames
        self.reducedReds = self.reduceAllFrames(self.masterbias,self.masterdark,self.masterflatred,self.redLights)
        ##reduce green light frames
        self.reducedGreens = self.reduceAllFrames(self.masterbias,self.masterdark,self.masterflatgreen,self.greenLights)
        ##reduce blue light frames
        self.reducedBlues = self.reduceAllFrames(self.masterbias,self.masterdark,self.masterflatblue,self.blueLights)
        
    def stackAutomatic(self):

        ##stack red light frames
        self.stackedRedFrame = self.stackColor(self.reducedReds)
        ##stack green light frames
        self.stackedGreenFrame = self.stackColor(self.reducedGreens)
        ##stack blue light frames
        self.stackedGreenFrame = self.stackColor(self.reducedBlues)




    def postprocessaesthetic(self):
        '''for i in range(len(masterreds)):
            for j in range(len(masterreds[i])):
                exceed = 5.0
                if masterreds[i][j] ==0 or mastergreens[i][j] == 0 or masterblues[i][j] ==0:
                    continue
                if masterreds[i][j]/mastergreens[i][j] > exceed or masterreds[i][j]/masterblues[i][j] >exceed or mastergreens[i][j]/masterreds[i][j] > exceed or mastergreens[i][j]/masterblues[i][j] >exceed or masterblues[i][j]/masterreds[i][j] > exceed or masterblues[i][j]/mastergreens[i][j] >exceed:


                    masterreds[i][j] = rmean#or neighboring pixels average.
                    mastergreens[i][j] = gmean
                    masterblues[i][j] = bmean
        '''
        pass

        ##stacking
        ##cosmic rays removal.
