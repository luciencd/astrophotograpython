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
    def __init__(self,filter,frame):
        Frame.__init__(self)
        self.filter = filter_
        self.frames.append(frame)

    def getFilter(self):
        return self.filter

    def createMaster(self):
        return self.frames[0][0].data



class Dark(Frame):
    def __init__(self,frames):
        Frame.__init__(self)
        for frame in frames:
            self.frames.append(frame)

    def getNpArrays(self):
        return map(lambda x: x[0].data,self.frames)

    def createMaster(self):
        ##numpy stuff to create master dark.
        nparrays = self.getNpArrays()
        nparrayaverage = np.average(nparrays,axis=0)
        return nparrayaverage

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

    def createMaster(self):
        nparrays = self.getNpArrays()
        nparrayaverage = np.average(nparrays,axis=0)
        return nparrayaverage

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



class Stack:
    def __init__(self,masterbias,masterdark):
        self.masterbias = masterbias##single frame
        self.masterdark = masterdark##single frame


class RBGstack:
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
        ##Bias substraction
        ##Dark substraction
        ##Flat Division
        ##OFFSETTING
        ##stacking
        ##cosmic rays removal.
        pass





#IMPORTING
source = '../../../dropbox/astrohirsch/FridayNight/'
red = fits.open(source+'RingNEBULA-0132.fit')
print red[0].header

darks = [fits.open(source+'RingNEBULA-009Dark5.fit'),fits.open(source+'RingNEBULA-010Dark5.fit')]
dark_frame = Dark(darks)
dark_frame.createMaster()
