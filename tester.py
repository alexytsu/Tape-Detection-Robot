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
COLOR_LOOKUP = None

go = 95

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

def mask_lookup(image):
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
    result = np.take(COLOR_LOOKUP, Index)
    return result

def show_canny(frame):
    dimensions = frame.shape
    downsize = cv2.resize(frame, (0,0), fx=0.1, fy=0.1)
    edges = cv2.Canny(downsize, 40, 250)
    edges = cv2.resize(edges, (dimensions[1], dimensions[0]))
    cv2.imshow("hello", edges)
    return edges


def test_model(model_name):




    # load the video file
    if CAMERA:
        video = WebcamVideoStream(src=0).start()

    else:
        # video_file_path = os.path.join("footage", choose_file())
        # video = cv2.VideoCapture(video_file_path)
        video = cv2.VideoCapture("./footage/MCIC_variable.mkv")

    frame_n = 0
    smoother = AngleBuffer(1)
    while True:
        frame = None
        if CAMERA:
            frame = video.read()
            frame = applyIPT(frame)
        else:
            retval, frame = video.read()
            if not retval:
                pass
    
        # preprocess
        edges = show_canny(frame)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        frame = edges & frame

        # resize
        w = 300
        h = 300
        frame = cv2.resize(frame, (w, h))

        # classify
        other_ynew = mask_lookup(frame)
        # ynew = mask_image(frame, model, frame_n)

        # show_masks(other_ynew, frame, "lookup")
        # show_masks(ynew, frame, "predict")

        try:
            angle,speed = plan_steering(other_ynew, frame)
        except:
            angle = 0
            speed = 94
        smoother.add_new(angle)
        angle = smoother.get_angle()
        if go == 95:
            go == 96
        else:
            go == 95
        if SER:
            SendSpeed(SER, int(angle), go)

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

    # load the model
    model_file_path = os.path.join("trained_models", "Gaussian", "model.sav")
    model_file = open(model_file_path, "rb")
    model = pickle.load(model_file)

    COLOR_LOOKUP = np.zeros((256,256), dtype= np.uint8)

    for h in range(256):
        for s in range(256):
            answers = ["NONE", "BLUE", "RED", "YELLOW", "OTHER"]
            result =  model.predict([np.array([h,s])])[0]
            if result == 1 or result == 3:
                print(f"Storing H:{h} with S:{s} as {answers[result]} {result}")
            COLOR_LOOKUP[s][h] = int(result)


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

