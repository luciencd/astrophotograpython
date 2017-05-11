'''
offsets = [[[originalx,originaly],  [511,709],[498,707]],\
            [[522,711],             [508,709],[493,706]],\
            [[522,714],             [503,708],[488,705]]]
            '''

def offsetter(length,dim,dx,dy,sx,sy,fx,fy):
    x = x0 = sx
    y = y0 = sy

    arr = []
    for i in range(dim):
        arr.append([])

        for j in range(length):
            x = int(x0+dx*i+dx*(j+1))
            y = int(y0+dy*i+dy*(j+1))
            arr[i].append([x,y])

    for i in range(dim):
        for j in range(len(arr)):
            arr[i][j][0] += int(fx*i)
            arr[i][j][1] += int(fy*i)

    return arr

#print offsetter(3,3,-4,-1,532,713)
