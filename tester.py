import os
import pickle
import argparse
import pdb
import sys
import math

import cv2
import numpy as np
from matplotlib import pyplot as plt

from utility import choose_file
from fr import PyFrame
from arduino import getSerialPort, SendSpeed
from helper import show_masks, writeLineAttributes
from nav import plan_steering, getLineAttributes

DEBUG = True
CAMERA = True
SER = None
MAPPING = None
TRANSLATION = None
SHOW_CAMERA = False

def applyIPT(image):
    sliderMax = 800
    rows = image.shape[0]
    cols = image.shape[1]
    image = cv2.warpPerspective(image, MAPPING, (int(4*image.shape[1]), 4*image.shape[0]))
    X, Y, Theta = TRANSLATION
    M = np.float32([[1,0,X-int(sliderMax/2)],[0,1,Y-int(sliderMax/2)]])
    image = cv2.warpAffine(image, M, (cols, rows))
    M = cv2.getRotationMatrix2D((cols/2, rows/2), Theta-90,1)
    image = cv2.warpAffine(image, M, (cols, rows))
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

    return model.predict(Xnew)

    retval = 0

    if navLine is not None:
        print("nav")
        lat, angle, steer = getLineAttributes(navLine)
        writeLineAttributes(lat, angle, steer, image)
        retval = steer
    elif blueLine and yellowLine:
        print("blue + yellow")
        lat1, angle1, steer1 = getLineAttributes(blueLine)
        lat2, angle2, steer2 = getLineAttributes(yellowLine)
        lat = (lat1 + lat2) / 2
        angle = (angle1 + angle2) / 2
        steer = (steer1 + steer2) / 2
        writeLineAttributes(lat, angle, steer, image)
        retval = steer
    elif blueLine:
        print("blue")
        lat, angle, steer = getLineAttributes(blueLine)
        writeLineAttributes(lat, angle, steer, image)
        retval = 2.5 * steer
    elif yellowLine:
        print("yellow")
        lat, angle, steer = getLineAttributes(yellowLine)
        writeLineAttributes(lat, angle, steer, image)
        retval = 2.5 * steer
    if SHOW_CAMERA:
        cv2.imshow("res", cv2.resize(image, (1280, 720)))
        if CAMERA:
            cv2.waitKey(1)
        else:
            if cv2.waitKey(0) & 0xFF == ord("q"):
                exit()
    return retval




def test_model(model_name):
    # load the model
    model_file_path = os.path.join("trained_models", model_name, "model.sav")
    model_file = open(model_file_path, "rb")
    model = pickle.load(model_file)

    # load the video file
    if CAMERA:
        video = cv2.VideoCapture(4)
    else:
        video_file_path = os.path.join("footage", choose_file())
        video = cv2.VideoCapture(video_file_path)

    frame_n = 0
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            print("Video finished")
            break
    
        #frame = applyIPT(frame)

        frame = cv2.resize(frame, (128, 72))
        ynew = mask_image(frame, model, frame_n)
        angle = plan_steering(ynew, frame)
        if SER:
            SendSpeed(SER, int(angle), 90)

        frame_n += 1


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
        ipm_file = open('../IPMtest/homographyMatrix.p', 'rb')
        trans_file = open('../IPMtest/source/Translation.p', 'rb')
        MAPPING = pickle.load(ipm_file)
        TRANSLATION = pickle.load(trans_file)
    except:
        MAPPING = None
    test_model("Gaussian")

