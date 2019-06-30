#distutils: language = c++
#distutils: sources = Frame.cpp

from libcpp.vector cimport vector
from libcpp.pair cimport pair
from libcpp cimport bool

cdef extern from "Frame.h" namespace "frame":
    cdef cppclass Frame:
        Frame(vector[vector[double]]) except +
        vector[vector[double]] arr;
        vector[pair[int, int]] lightvec
        vector[pair[int, int]] darkvec
        double percentage;
        vector[pair[int, int]] getMidPoints()
        vector[pair[int, int]] getTapePoints(bool)
        vector[pair[int, int]] getDarkPoints()
        vector[pair[int, int]] getLightPoints()
        vector[pair[pair[int, int], pair[int, int]]] getBlueLine()
        vector[pair[pair[int, int], pair[int, int]]] getYellowLine()
        vector[pair[pair[int, int], pair[int, int]]] getNavLine()

cdef class PyFrame:
    cdef Frame *thisptr
    def __cinit__(self, vector[vector[double]] arr):
        self.thisptr = new Frame(arr)
    
    def __dealloc__(self):
        del self.thisptr
    
    def getMidPoints(self):
        return self.thisptr.getMidPoints()

    def getTapePoints(self, top):
        return self.thisptr.getTapePoints(top)

    def getBlueLine(self):
        return self.thisptr.getBlueLine()

    def getYellowLine(self):
        return self.thisptr.getYellowLine()

    def getDarkPoints(self):
        return self.thisptr.getDarkPoints()

    def getLightPoints(self):
        return self.thisptr.getLightPoints()

    def getNavLine(self):
        return self.thisptr.getNavLine()