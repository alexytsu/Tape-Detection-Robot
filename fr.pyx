#distutils: language = c++
#distutils: sources = Frame.cpp

from libcpp.vector cimport vector

cdef extern from "Frame.h" namespace "frame":
    cdef cppclass Frame:
        Frame(vector[vector[double]]) except +
        vector[vector[double]] arr;
        int getSize()

cdef class PyFrame:
    cdef Frame *thisptr
    def __cinit__(self, vector[vector[double]] arr):
        self.thisptr = new Frame(arr)
    
    def __dealloc__(self):
        del self.thisptr
    
    def getSize(self):
        return self.thisptr.getSize()