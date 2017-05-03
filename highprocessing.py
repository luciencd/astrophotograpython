import cv2
from matplotlib import pyplot as plt
import numpy as np

def norm(val,tmin,tmax,nmin,nmax):

    downrange = ((val-nmin))/(nmax-nmin)
    if(downrange<0):
        downrange = 0.0
    elif(downrange>1):
        downrange = 1.0
    uprange = downrange*(tmax-tmin)

    return uprange+tmin

#for mono, just take the average, and make a 3 slot array with copies.
class Grapher:

    def __init__(self):
        #self.data = np.array([redfinalstack_np,greenfinalstack_np,bluefinalstack_np])
        pass

    def plot(self,nmin,nmax,data):
        #data = data.swapaxes(0,2)
        #data = np.array(map(lambda color: map(lambda row: map(lambda cell: 0 if cell<0 else cell,row),color),data))
        print "minimum:",data


        #gray_data = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY) # from (5x5x3) to (5x5) matrix, perfect for plotting!
        #np.ndarray(shape=(2,2), dtype=float, order='F')
        colordata = np.ndarray(shape = (len(data[0]),len(data[0][0]),3))
        #print len(data[0]),len(data[0][0])
        #print colordata
        for x in range(len(data[0])):
            for y in range(len(data[0][x])):
                ##map to 0-255 based on nmin and nmax
                color = np.array([norm(data[0][x][y],0.0,1.0,nmin,nmax),norm(data[1][x][y],0.0,1.0,nmin,nmax),norm(data[2][x][y],0.0,1.0,nmin,nmax)])
                #print color
                colordata[x][y][0] = color[0] #print colordata[x][y]
                colordata[x][y][1] = color[1]
                colordata[x][y][2] = color[2]
                # = 0
        plt.imshow(colordata)

    def centroids(self,centroids):

        xes = map(lambda x: x[0],centroids)
        yes = map(lambda x: x[1],centroids)
        zes = map(lambda x: x[2],centroids)

        plt.scatter(xes,yes)
    def finish(self):
        plt.xticks([])
        plt.yticks([])
        plt.show()

'''
class CentroidGrapher(grapher):
    def __init__(self,redfinalstack_np,greenfinalstack_np,bluefinalstack_np,centroids):
        super(self,redfinalstack_np,greenfinalstack_np,bluefinalstack_np)

class HRGrapher(grapher):
    def __init__(self,redfinalstack_np,greenfinalstack_np,bluefinalstack_np,stars):
        super(self,redfinalstack_np,greenfinalstack_np,bluefinalstack_np)'''

class Analyzer:
    def __init__(self,redfinalstack_np,greenfinalstack_np,bluefinalstack_np):
        self.redfinalstack_np = redfinalstack_np
        self.greenfinalstack_np = greenfinalstack_np
        self.bluefinalstack_np = bluefinalstack_np

        #virtual floodfill
        self.locations_visited = []
        #centroid list.
    def averageStack(self,redfinalstack_np,greenfinalstack_np,bluefinalstack_np):
        stack = np.average(np.array([redfinalstack_np,greenfinalstack_np,bluefinalstack_np]),axis = 0)
        return stack
    def floodfill(self,x,y):

        return monostack

    def cutoff(self,minimum,redfinalstack_np,greenfinalstack_np,bluefinalstack_np):
        ##average up all stacks
        stack = np.average(np.array([redfinalstack_np,greenfinalstack_np,bluefinalstack_np]),axis = 0)
        print stack
        monostack = map(lambda row: map(lambda cell: 0 if (cell < minimum) else 1,row),stack)
        return monostack

    def floodfill(self,stack,x,y,lightlimit,sizelimit):

        print(len(stack[0]),len(stack))
        locations_visited = np.full((len(stack),len(stack[0])),0)
        #print locations_visited

        if(stack[y][x]>lightlimit):
            locations_visited[y][x] = 1
        else:
            return []


        ## [(50,50)]
        places_stack = [[x,y,stack[y][x]]]
        locations_list = []
        #print places_stack
        while(len(places_stack)>0):
            place = places_stack[0]
            #print "PLACES_STACK:",places_stack

            x = place[0]
            y = place[1]

            #print y,x,stack[y][x]
            if(y+1<len(stack)):

                if((locations_visited[y+1][x] == 0) and stack[y+1][x] > lightlimit):
                    places_stack.append([x,y+1,stack[y+1][x]])
                    locations_visited[y+1][x] = 1
                    self.locations_visited[y+1][x] = 1
                    locations_list.append([x,y+1,stack[y+1][x]])

            if(y-1>=0):

                if((locations_visited[y-1][x] == 0) and stack[y-1][x] > lightlimit):
                    places_stack.append([x,y-1,stack[y-1][x]])
                    locations_visited[y-1][x] = 1
                    self.locations_visited[y-1][x] = 1
                    locations_list.append([x,y-1,stack[y-1][x]])

            if(x+1<len(stack[0])):

                if((locations_visited[y][x+1] == 0) and stack[y][x+1] > lightlimit):
                    places_stack.append([x+1,y,stack[y][x+1]])
                    locations_visited[y][x+1] = 1
                    self.locations_visited[y][x+1] = 1
                    locations_list.append([x+1,y,stack[y][x+1]])

            if(x-1>=0):

                if((locations_visited[y][x-1] == 0) and stack[y][x-1] > lightlimit):
                    places_stack.append([x-1,y,stack[y][x-1]])
                    locations_visited[y][x-1] = 1
                    self.locations_visited[y][x-1] = 1
                    locations_list.append([x-1,y,stack[y][x-1]])

            places_stack = places_stack[1:]


        #print locations_list

        return locations_list

        #current_locations = self.floodfillascent(stack,x,y,[],0)
        #print "length of current_locations:",len(current_locations)
        #print "current_locations:",current_locations
    def backgroundCounts(self,stack_color_np):
        flatcounts = stack_color_np.flatten(order="C")
        flatcounts = sorted(flatcounts)
        return sum(flatcounts[0:len(flatcounts)/5])/len(flatcounts)


    def starFluxColor(self,stack_color_np,x,y,r):
        summation = 0.0
        for row in range(r-y,r+y):
            for col in range(r-x,r+x):
                if (col-x)**2 + (row-y)**2 < r:
                    summation += stack_color_np[row][col]
        return summation


    def starFlux(self,stack_color,x,y,r):
        if(stack_color == "R"):
            return self.starFluxColor(self.redfinalstack_np,x,y,r)

        if(stack_color == "G"):
            return self.starFluxColor(self.greenfinalstack_np,x,y,r)

        if(stack_color == "B"):
            return self.starFluxColor(self.bluefinalstack_np,x,y,r)

        if(stack_color == "V"):
            return self.starFluxColor(self.redfinalstack_np,x,y,r)+self.starFluxColor(self.greenfinalstack_np,x,y,r)+self.starFluxColor(self.bluefinalstack_np,x,y,r)

    def centroid(self,stack,x,y,sizelimit,CUTOFF_VALUE):
        #print "Starting my centroid"
        #return [x,y,1.0]
        floodfilllist = self.floodfill(stack,x,y,CUTOFF_VALUE,sizelimit)

        if floodfilllist == [] or len(floodfilllist)<sizelimit:
            return []
        print len(floodfilllist)

        ##now get the HM.
        maxflood = max(floodfilllist,key = lambda x:x[2])

        ##now get the FWHM

        ##get it for band B and band V

        ##add both values to tuple.
        ##OR just use a radius of ten circle and sum all the values in it.

        return maxflood

    def centroids(self,stack,sizelimit,CUTOFF_VALUE):
        #stack = self.cutoff(stack,stack,stack,450)
        ##average of all colors to center.
        self.locations_visited = np.ndarray(shape=(len(stack),len(stack[0])))
        centroid_list = []
        #stack = np.swapaxes(stack, 0, 1)
        for y in range(0,len(stack),5):
            for x in range(0,len(stack[y]),5):
                if self.locations_visited[y][x]==1:
                    print "already seen"
                    continue
                if stack[y][x] < CUTOFF_VALUE:
                    continue
                #print x,y
                centroid = self.centroid(stack,x,y,sizelimit,CUTOFF_VALUE)
                if centroid == []:
                    pass
                else:
                    print "centroid:",centroid
                    if(centroid not in centroid_list):
                        centroid_list.append(centroid)

        return sorted(centroid_list,key = lambda x: -x[2])



    #def save(self,zipdest,target,redfinalstack_np,greenfinalstack_np,bluefinalstack_np):
