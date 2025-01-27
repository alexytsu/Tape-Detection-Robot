from threading import Thread

import cv2
import numpy as np
import pickle
import time

class WebcamVideoStream:
    """ 
    Streams a video from a camera source as a separate thread so as not to block on I/O
    :param src: An integer specifying which camera we read from
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.stream.set(cv2.CAP_PROP_FPS, 60)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.frame_number = 0
        self.last_sent = 0

    def start(self):
        print("starting camera...")
        Thread(target=self.update, args=()).start()
        print("camera thread started")
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()
            if(self.grabbed):
                self.frame_number += 1

    def read(self):
        return self.frame, self.frame_number

    def stop(self):
        self.stopped = True

def applyIPT(image, mapping, translation, crop):
    sliderMax = 1000
    rows = 720
    cols = 480
    image = cv2.warpPerspective(image, mapping, (int(4*image.shape[1]), 4*image.shape[0]))
    X, Y, Theta = translation
    M = np.float32([[1,0,X-int(sliderMax/2)],[0,1,Y-int(sliderMax/2)]])
    image = cv2.warpAffine(image, M, (cols, rows))
    M = cv2.getRotationMatrix2D((cols/2, rows/2), Theta-90,1)
    image = cv2.warpAffine(image, M, (cols, rows))
    xB, xE, yB, yE = crop
    image = image[yB:yE,xB:xE]
    return image

def mask_lookup(image, color_table):
    """
    Use a lookup table to see if there

    """
    hue_and_sat = image[:,:,0:2]

    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    H = hsvImage[:, :, 0]
    S = hsvImage[:, :, 1]

    # find how long the one dimensional form needs to be
    one_dim_length = hsvImage.shape[0] * hsvImage.shape[1]

    # now spread out the image [HSV]
    Xnew = np.reshape(hsvImage, (one_dim_length, 3))

    # only take H and S
    Hue = Xnew[:, 0]
    Sat = Xnew[:, 1]

    Index = Hue + 256 * Sat
    result = np.take(color_table, Index)
    return result

def get_edges(frame, show_debug):
    dimensions = frame.shape
    edges = cv2.Canny(frame, 50, 250)
    kernel = np.ones((5,5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=4 )
    return edges

def get_color_lookup(filename="LOOKUP.pkl"):
    try:
        lookup_file = open("./LOOKUP.pkl", 'rb')
    except:
        raise Exception("No lookup table was trained")
    lookup_table = pickle.load(lookup_file)
    return lookup_table

def get_perspective_warp():
    ipm_file = open('../IPMtest/source/homographyMatrix.p', 'rb')
    trans_file = open('../IPMtest/source/Translation.p', 'rb')
    crop_file = open('../IPMtest/source/Crop.p', 'rb')
    crop_other = open('../IPMtest/source/CropSecond.p', 'rb')
    inverse_map = pickle.load(ipm_file)
    translation = pickle.load(trans_file)
    crop_boundaries = pickle.load(crop_file)
    crop2_boundaries = pickle.load(crop_other)
    return inverse_map, translation, crop_boundaries, crop2_boundaries


