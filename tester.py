import os
import pickle
import argparse
import pdb
import sys
import math
from threading import Thread

import cv2
import numpy as np
from matplotlib import pyplot as plt

from utility import choose_file
from fr import PyFrame
from arduino import getSerialPort, SendSpeed
from helper import show_masks, writeLineAttributes
from nav import plan_steering, getLineAttributes, CAMERA, AngleBuffer

DEBUG = True
SER = None
MAPPING = None
TRANSLATION = None
CROP = None

class WebcamVideoStream:
    def __init__(self, src = 0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

def applyIPT(image):
    sliderMax = 1000
    rows = image.shape[0]
    cols = image.shape[1]
    image = cv2.warpPerspective(image, MAPPING, (int(4*image.shape[1]), 4*image.shape[0]))
    X, Y, Theta = TRANSLATION
    M = np.float32([[1,0,X-int(sliderMax/2)],[0,1,Y-int(sliderMax/2)]])
    image = cv2.warpAffine(image, M, (cols, rows))
    M = cv2.getRotationMatrix2D((cols/2, rows/2), Theta-90,1)
    image = cv2.warpAffine(image, M, (cols, rows))
    xB, xE, yB, yE = CROP
    image = image[yB:yE,xB:xE]
    return image

def mask_image(image, model, frame_n):
    if DEBUG:
        print("Analysing frame", frame_n)

    # Convert BGR to HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    H = hsvImage[:, :, 0]
    S = hsvImage[:, :, 1]

    # find how long the one dimensional form needs to be
    one_dim_length = hsvImage.shape[0] * hsvImage.shape[1]

    # now spread out the image [HSV]
    Xnew = np.reshape(hsvImage, (one_dim_length, 3))

    # only take H and S
    Xnew = Xnew[:, 0:2]
    result = model.predict(Xnew)
    return result


def test_model(model_name):
    # load the model
    model_file_path = os.path.join("trained_models", model_name, "model.sav")
    model_file = open(model_file_path, "rb")
    model = pickle.load(model_file)

    # load the video file
    if CAMERA:
        video = WebcamVideoStream(src=0).start()

    else:
        video_file_path = os.path.join("footage", choose_file())
        video = cv2.VideoCapture(video_file_path)
        # video = cv2.VideoCapture("./footage/marsfield_02.mkv")

    frame_n = 0
    smoother = AngleBuffer(3)
    while True:
        frame = None
        if CAMERA:
            frame = video.read()
            frame = applyIPT(frame)
        else:
            retval, frame = video.read()
            if not retval:
                pass
    

        w = 300
        h = 300
        frame = cv2.resize(frame, (w, h))
        ynew = mask_image(frame, model, frame_n)
        angle = plan_steering(ynew, frame)
        smoother.add_new(angle)
        angle = smoother.get_angle()
        print("SeRIAL", SER, "angle", angle)
        if SER:
            SendSpeed(SER, int(angle), 90)

        frame_n += 1

    print("fin")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Running with CAMERA mode on by default")
        print("Use 'python tester.py --test' to use a saved video")
    else:
        if sys.argv[1] == "--test":
            CAMERA = False
    try:
        SER = getSerialPort()
    except:
        SER = None

    try:
        ipm_file = open('../IPMtest/source/homographyMatrix.p', 'rb')
        trans_file = open('../IPMtest/source/Translation.p', 'rb')
        crop_file = open('../IPMtest/source/Crop.p', 'rb')
        MAPPING = pickle.load(ipm_file)
        TRANSLATION = pickle.load(trans_file)
        CROP = pickle.load(crop_file)
    except:
        MAPPING = None
    test_model("Gaussian")

