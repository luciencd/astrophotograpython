import math
def getMagnitude(FluxT,FluxK,MagK):
    try:
        print FluxT,"/",FluxK,": MagK",MagK
        return -2.5*math.log(FluxT/FluxK,10)+MagK
    except ValueError:
        return 0

def absoluteMag(mag1,D1):
    return (-5)*math.log(D1/10.0,10)+mag1
