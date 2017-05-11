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

def export(zipdest,target,data):
    ##TODO: remove file directory dependency

    try:
        os.remove(zipdest+target+".fit")
    except OSError:
        pass
    print "Removed file."
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
        self.lightframe = lightframe
        self.reduced_np = reduced_np

    def getFilter(self):
        return self.lightframe.filter_

    def createMaster(self):
        return self.reduced_np

    def trackingStar(self,x,y):
        self.lightframe.trackingStar(x,y)

    def getStarx(self):
        return self.lightframe.getStarx()

    def getStary(self):
        return self.lightframe.getStary()

class StackedFrame(Frame):#reducedframe self input is a light frame.
    def __init__(self,reduced_np,lightframe):
        Frame.__init__(self)
        self.lightframe = lightframe
        self.reduced_np = reduced_np

    def getFilter(self):
        return self.lightframe.filter_

    def createMaster(self):
        return self.reduced_np

    def trackingStar(self,x,y):
        self.lightframe.trackingStar(x,y)

    def getStarx(self):
        return self.lightframe.getStarx()

    def getStary(self):
        return self.lightframe.getStary()

class Stacker:
    def __init__(self,masterbias,masterdark):
        self.masterbias = masterbias##single frame
        self.masterdark = masterdark##single frame


class RGBStacker(Stacker):
    def __init__(self,masterbias,masterdark,masterflatred,masterflatgreen,masterflatblue,redLights,greenLights,blueLights):
        Stacker.__init__(self,masterbias,masterdark)
        self.masterflatred = masterflatred
        self.masterflatgreen = masterflatgreen
        self.masterflatblue = masterflatblue
        self.redLights = redLights
        self.greenLights = greenLights
        self.blueLights = blueLights
        self.starx = redLights[0].getStarx()
        self.stary = redLights[0].getStary()

    ##simple function that superimposes two pictures with their cartesian union as the end dimensions.
    ##TODO: function that creates composite images.
    def offset(self,frame,x1,y1,x2,y2):
        offsetframe = copy.deepcopy(frame)

        width = frame.shape[0]
        height = frame.shape[1]
        for row in range(0,width-int(math.fabs(y1-y2))):
            for cell in range(0,height-int(math.fabs(x1-x2))):
                offsetframe[row][cell] = frame[row+(y1-y2)][cell+(x1-x2)]

        return offsetframe

    ## function creates and processes all the processing frames required for reduction
    def generateMasters(self):
        ##Bias substraction
        self.masterbias_np = self.masterbias.createMaster()

        ##Dark substraction
        self.masterdark_np = self.masterdark.createMaster(self.masterbias_np,self.masterdark.getExposure()/self.redLights[0].getExposure())##GENERIC DARK FRAME!!! because of binning, impossible to combine the two

        ##Flat normalization
        self.masterflatred_np = self.masterflatred.createMaster(self.masterbias_np,np.multiply(self.masterdark_np,self.masterflatred.getExposure()/self.masterdark.getExposure()))

        self.masterflatgreen_np = self.masterflatgreen.createMaster(self.masterbias_np,np.multiply(self.masterdark_np,self.masterflatgreen.getExposure()/self.masterdark.getExposure()))

        self.masterflatblue_np = self.masterflatblue.createMaster(self.masterbias_np,np.multiply(self.masterdark_np,self.masterflatblue.getExposure()/self.masterdark.getExposure()))

    ##takes in bias, dark and flat Numpy arrays, and single light(Frame) object, and returns ReducedFrame(Frame)
    def reduceFrame(self,masterbias_np,masterdark_np,masterflat_np,lightframe):
        masterlight_np = lightframe.createMaster()##gets the one frame

        masterlight_np = np.subtract(masterlight_np,masterbias_np)
        masterlight_np = np.subtract(masterlight_np,masterdark_np)
        masterlight_np = np.divide(masterlight_np,masterflat_np)

        reduced_frame = ReducedFrame(masterlight_np,lightframe)
        return reduced_frame

    ##takes list of bias, dark and flat Numpy arrays, and single light(Frame) object, and returns ReducedFrame(Frame)
    def reduceAllFrames(self,masterbias_np,masterdark_np,masterflat_np,lightframes):
        ##TODO:ensure the exposure time is equal where it matters.
        ##TODO:ensure the filters line up.
        return map(lambda f: self.reduceFrame(masterbias_np,masterdark_np,masterflat_np,f),lightframes)

    def stackColor(self,reduced_lights):
        masteroffset_list = []

        for i in range(len(reduced_lights)):
            masterframe = reduced_lights[i]
            originalframe = reduced_lights[0]
            masterframe_np = masterframe.createMaster()
            masteroffset_list.append(self.offset(masterframe_np,masterframe.getStarx(),masterframe.getStary(),self.starx,self.stary))

        ##can change funtion from average to median to affect how final stacks come out.
        masteroffset_np = np.median(masteroffset_list,axis=0)
        return StackedFrame(map(lambda y: map(lambda x: max(0.0,x),y),masteroffset_np),reduced_lights[0])

    ##automatically reduces the images.
    def reduceAutomatic(self):
        ##generateMasters
        self.generateMasters()

        ##reduce red light frames
        self.reducedReds = self.reduceAllFrames(self.masterbias_np,self.masterdark_np,self.masterflatred_np,self.redLights)
        ##reduce green light frames
        self.reducedGreens = self.reduceAllFrames(self.masterbias_np,self.masterdark_np,self.masterflatgreen_np,self.greenLights)
        ##reduce blue light frames
        self.reducedBlues = self.reduceAllFrames(self.masterbias_np,self.masterdark_np,self.masterflatblue_np,self.blueLights)

    ##automatically stacks the images.
    def stackAutomatic(self):

        ##stack red light frames
        self.stackedRedFrame = self.stackColor(self.reducedReds)
        ##stack green light frames
        self.stackedGreenFrame = self.stackColor(self.reducedGreens)
        ##stack blue light frames
        self.stackedBlueFrame = self.stackColor(self.reducedBlues)

    #requires reduceAutomatic and stackAutomatic to be run.
    def getFinal(self):
        ## TODO: create a bunch of these functions to return all the reduced and stacked frames done by this class.
        pass

    ## for cosmic ray removal.
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
        ##cosmic rays removal.
