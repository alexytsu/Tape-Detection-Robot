#distutils: language = c++
#distutils: sources = Frame.cpp

from libcpp.vector cimport vector
from libcpp.pair cimport pair

cdef extern from "Frame.h" namespace "frame":
    cdef cppclass Frame:
        Frame(vector[vector[double]]) except +
        vector[vector[double]] arr;
        vector[pair[int, int]] lightvec
        vector[pair[int, int]] darkvec
        vector[pair[int, int]] getPoints()
        vector[pair[pair[int, int], pair[int, int]]] getLines()

cdef class PyFrame:
    cdef Frame *thisptr
    def __cinit__(self, vector[vector[double]] arr):
        self.thisptr = new Frame(arr)
    
    def __dealloc__(self):
        del self.thisptr
    
    def getPoints(self):
        return self.thisptr.getPoints()

    def getLines(self):
        return self.thisptr.getLines()