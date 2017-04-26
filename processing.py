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


class Light(Frame):
    ##filter is Filter(Enum) frame is fits file opened
    def __init__(self,filter,frame):
        Frame.__init__(self)
        self.filter = filter
        self.frames.append(frame)

    def getLight(self):
        return self.frames[0][0].data

    def getFilter(self):
        return self.filter



class Dark(Frame):
    def __init__(self):
        Frame.__init__(self,frames)
        for frame in frames:
            self.frames.append(frame)

    def createMaster(self):
        ##numpy stuff to create master dark.
        pass


class Flat(Frame):
    def __init__(self):
        
class Stack:
    def __init__(self):
        self.biasframes = []
        self.darkframes = []
        self.flatframes = []
