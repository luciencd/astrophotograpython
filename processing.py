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

    def getFilter(self):
        return self.filter_

    def createMaster(self):
        return np.array(self.frames[0][0].data)

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




class Stack:
    def __init__(self,masterbias,masterdark):
        self.masterbias = masterbias##single frame
        self.masterdark = masterdark##single frame


class RGBStack(Stack):
    def __init__(self,masterbias,masterdark,masterflatred,masterflatgreen,masterflatblue,redLights,greenLights,blueLights,offsets,originalx,originaly):
        Stack.__init__(self,masterbias,masterdark)
        self.masterflatred = masterflatred
        self.masterflatgreen = masterflatgreen
        self.masterflatblue = masterflatblue
        self.redLights = redLights
        self.greenLights = greenLights
        self.blueLights = blueLights
        self.offsets = offsets
        self.originalx = originalx
        self.originaly = originaly

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
    def reduce(self):
        ##TODO:ensure the exposure time is equal where it matters.
        ##TODO:ensure the filters line up.

        ##Bias substraction
        masterbias_np = self.masterbias.createMaster()
        ##Dark substraction
        #masterdark_np = self.masterdark.createMaster(masterbias_np)
        masterdark_np = self.masterdark.createMaster(masterbias_np,self.masterdark.getExposure()/self.redLights[0].getExposure())##GENERIC DARK FRAME!!! because of binning, impossible to combine the two

        export(masterdark_np,"results/","masterdark")
        ##Flat Division #red is 5 seconds, dark is 30 seconds.

        masterflatred_np = self.masterflatred.createMaster(masterbias_np,np.multiply(masterdark_np,self.masterflatred.getExposure()/self.masterdark.getExposure()))
        #print "dark red differences:",np.multiply(masterdark_np,self.masterflatred.getExposure()/self.masterdark.getExposure())
        masterflatgreen_np = self.masterflatgreen.createMaster(masterbias_np,np.multiply(masterdark_np,self.masterflatgreen.getExposure()/self.masterdark.getExposure()))
        #print "dark green differences:",np.multiply(masterdark_np,self.masterflatgreen.getExposure()/self.masterdark.getExposure())
        masterflatblue_np = self.masterflatblue.createMaster(masterbias_np,np.multiply(masterdark_np,self.masterflatblue.getExposure()/self.masterdark.getExposure()))


        ##single frame reduction(RED)
        masterreds = []
        for redlightframe in self.redLights:
            master_redlight_np = redlightframe.createMaster()##gets the one frame

            #TODO:dark corrections for exposure time of flat frame!
            #print "before bias removal",master_redlight_np
            master_redlight_np = np.subtract(master_redlight_np,masterbias_np)
            #print "after bias removal",master_redlight_np
            master_redlight_np = np.subtract(master_redlight_np,masterdark_np)
            master_redlight_np = np.divide(master_redlight_np,masterflatred_np)
            masterreds.append(master_redlight_np)

        ##single frame reduction (GREEN)
        mastergreens = []
        for greenlightframe in self.greenLights:
            master_greenlight_np = greenlightframe.createMaster()##gets the one frame

            master_greenlight_np = np.subtract(master_greenlight_np,masterbias_np)
            master_greenlight_np = np.subtract(master_greenlight_np,masterdark_np)
            master_greenlight_np = np.divide(master_greenlight_np,masterflatgreen_np)
            mastergreens.append(master_greenlight_np)

        ##single frame reduction (BLUE)
        masterblues = []
        for bluelightframe in self.blueLights:
            master_bluelight_np = bluelightframe.createMaster()##gets the one frame

            master_bluelight_np = np.subtract(master_bluelight_np,masterbias_np)
            master_bluelight_np = np.subtract(master_bluelight_np,masterdark_np)
            master_bluelight_np = np.divide(master_bluelight_np,masterflatblue_np)
            masterblues.append(master_bluelight_np)

        ##OFFSETTING
        masteroffsetredframes = []
        masteroffsetgreenframes = []
        masteroffsetblueframes = []



        offsetred = self.offsets[0]
        offsetgreen = self.offsets[1]
        offsetblue = self.offsets[2]

        i = 0
        for masterredframe_np in masterreds:
            masteroffsetredframes.append(self.offset(masterredframe_np,offsetred[i][0],offsetred[i][1],self.originalx,self.originaly))
            i+=1
        i = 0
        for mastergreenframe_np in mastergreens:
            masteroffsetgreenframes.append(self.offset(mastergreenframe_np,offsetgreen[i][0],offsetgreen[i][1],self.originalx,self.originaly))
            i+=1
        i = 0
        for masterblueframe_np in masterblues:
            masteroffsetblueframes.append(self.offset(masterblueframe_np,offsetblue[i][0],offsetblue[i][1],self.originalx,self.originaly))
            i+=1



        masterreds = np.median(masteroffsetredframes,axis=0)
        mastergreens = np.median(masteroffsetgreenframes,axis=0)
        masterblues = np.median(masteroffsetblueframes,axis=0)
        rmean = np.mean(masterreds)
        gmean = np.mean(mastergreens)
        bmean = np.mean(masterblues)
        map(lambda y: map(lambda x: max(0.0,x),y),masterreds)
        map(lambda y: map(lambda x: max(0.0,x),y),mastergreens)
        map(lambda y: map(lambda x: max(0.0,x),y),masterblues)

        for i in range(len(masterreds)):
            for j in range(len(masterreds[i])):
                exceed = 5.0
                if masterreds[i][j] ==0 or mastergreens[i][j] == 0 or masterblues[i][j] ==0:
                    continue
                if masterreds[i][j]/mastergreens[i][j] > exceed or masterreds[i][j]/masterblues[i][j] >exceed or mastergreens[i][j]/masterreds[i][j] > exceed or mastergreens[i][j]/masterblues[i][j] >exceed or masterblues[i][j]/masterreds[i][j] > exceed or masterblues[i][j]/mastergreens[i][j] >exceed:


                    masterreds[i][j] = rmean#or neighboring pixels average.
                    mastergreens[i][j] = gmean
                    masterblues[i][j] = bmean

        #masteroffsetredframes = masterreds
        #masteroffsetgreenframes = mastergreens
        #masteroffsetblueframes = masterblues

        return (masterreds,mastergreens,masterblues)


        ##stacking
        ##cosmic rays removal.
