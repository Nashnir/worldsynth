#!/usr/bin/python
# A simple implementation of the diamond-square fractal algorithm for
# random terrain generation.
#   depth - level of detail of terrain, where grid size is 2^depth+1
#   roughness - a roughness constant for how rough the terrain should be
#   waterlevel - the height level to render water at
#   sizex - the x size of the geometry
#   sizey - the z size of the geometry
#   scale - a scaling factor for the maximum y height of the geometry

import math, random, sys
from numpy import *
from progressbar import ProgressBar, Percentage, ETA

class DS():
    def __init__( self, depth=9, roughness=0.6, waterlevel=0.0, sizex=10.0, sizey=10.0, scale=1.0):
        # initialise arguments to constructor
        self.depth = int(depth)
        self.roughness = float(roughness)
        self.waterlevel = float(waterlevel)
        self.sizex=float(sizex)
        self.sizey=float(sizey)
        self.scale=float(scale)
        self.size = (1 << self.depth)+1         # grid size, 2^depth+1
        self.heightmap = zeros((self.size,self.size))
        widgets = ['Generating heightmap: ', Percentage(), ' ', ETA() ]
        self.pbar = ProgressBar(widgets=widgets, maxval=self.size*self.size)


    # Itterative terrain deformer using classic diamond-square algorithm.
    def run(self):
        # Seeds an initial random altitude for the four corners of the dataset.
        self.heightmap[0,0]                     = self.scale*(random.random()-0.5)
        self.heightmap[0,self.size-1]           = self.scale*(random.random()-0.5)
        self.heightmap[self.size-1,0]           = self.scale*(random.random()-0.5)
        self.heightmap[self.size-1,self.size-1] = self.scale*(random.random()-0.5)

        rough = self.roughness
        r = self.size-1

        # Diamond-square iterative implementation:
        for i in range(self.depth):
          s = r >> 1
          x = 0
          while ( x < self.size-1 ):
            y = 0
            while ( y < self.size-1 ):
              self.diamond( rough, x, y, r )
              y = y + r
            x = x + r

          if s > 0:
            x = 0
            while ( x < self.size ):
              y = (x + s) % r
              while ( y < self.size ):
                self.square( rough, x-s, y-s, r )
                y = y + r
              x = x + s
          rough = rough * self.roughness #0.5
          r = r >> 1
          self.pbar.update(i)

        # compress the range while maintaining ratio
        newMin = 0.0; newMax = 1.0;
        oldMin = 0.0; oldMax = 0.0
        for x in range(0,self.size):
            for y in range(0,self.size):
                if self.heightmap[x,y] < oldMin:
                    oldMin = self.heightmap[x,y]
                if self.heightmap[x,y] > oldMax:
                    oldMax = self.heightmap[x,y]
        for x in range(0,self.size):
            for y in range(0,self.size):
                self.heightmap[x,y] = (((self.heightmap[x,y] - oldMin) * (newMax-newMin)) / (oldMax-oldMin)) + newMin

        # trip up heightmap to be power of 2
        self.heightmap = delete(self.heightmap,1,0)
        self.heightmap = delete(self.heightmap,1,1)
        self.pbar.finish()

    def diamond( self, c, x, y, step ):
        if step > 1:
            half=step/2
            avg = ( self.heightmap[x][y] +
                    self.heightmap[x][y+step] +
                    self.heightmap[x+step][y] +
                    self.heightmap[x+step][y+step] ) / 4
            h = avg + self.scale * c * (random.random()-0.5)
            self.heightmap[x+half][y+half] = h

    def square( self, c, x, y, step ):
        num=0
        avg=0.0
        half=step/2
        if ( x >= 0 ):
            avg=avg+self.heightmap[x][y+half]
            num=num+1
        if ( y >= 0 ):
              avg=avg+self.heightmap[x+half][y]
              num=num+1
        if ( x+step < self.size ):
              avg=avg+self.heightmap[x+step][y+half]
              num=num+1
        if ( y+step < self.size ):
              avg=avg+self.heightmap[x+half][y+step]
              num=num+1

        h = avg/num + self.scale * c * (random.random()-0.5)
        self.heightmap[x+half][y+half] = h

#            if self.landMassPercent() < 0.15 or self.landMassPercent() > 0.85 or self.averageElevation() < 0.2 or self.averageElevation() > 0.8:
#                print "Rejecting map: retrying..."
#                self.heightmap = zeros((self.width,self.height))
#            else:
#                print "We have a winner!"
#                break


    def landMassPercent(self):
        return self.heightmap.sum() / (self.width * self.height)

    def averageElevation(self):
        return average(self.heightmap)

# runs the program
if __name__ == '__main__':
    print "Setting things up..."
    mda = DS()
    print "Thinking..."
    mda.run()
    print "done!"