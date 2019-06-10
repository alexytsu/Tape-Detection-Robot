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
from nav import plan_steering, getLineAttributes, CAMERA, SHOW_CAMERA, AngleBuffer
from vision import WebcamVideoStream, applyIPT, get_edges, mask_lookup

DEBUG = True
SER = None
MAPPING = None
TRANSLATION = None
CROP = None

go = 95

def test_model(model_name, COLOR_LOOKUP):

    # load the video file
    if CAMERA:
        video = WebcamVideoStream(src=0).start()
    else:
        video_file_path = os.path.join("footage", choose_file())
        video = cv2.VideoCapture(video_file_path)
        # video = cv2.VideoCapture("./footage/MCIC_variable.mkv")

    frame_n = 0
    smoother = AngleBuffer(1)
    while True:
        frame = None
        if CAMERA:
            frame = video.read()
            frame = applyIPT(frame)
        else:
            print("Loaded video file")
            retval, frame = video.read()
            if not retval:
                pass
                

        # resize
        w = 300
        h = 300
        frame = cv2.resize(frame, (w, h))
    
        # preprocess
        edges = get_edges(frame)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        frame = edges & frame


        # classify
        other_ynew = mask_lookup(frame, COLOR_LOOKUP)

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
    """
    model_file_path = os.path.join("trained_models", "Gaussian", "model.sav")
    model_file = open(model_file_path, "rb")
    model = pickle.load(model_file)
    """

    lookup_file = open("./LOOKUP.pkl", 'rb')
    ipm_file = open('../IPMtest/source/homographyMatrix.p', 'rb')
    trans_file = open('../IPMtest/source/Translation.p', 'rb')
    crop_file = open('../IPMtest/source/Crop.p', 'rb')
    COLOR_LOOKUP = pickle.load(lookup_file)
    MAPPING = pickle.load(ipm_file)
    TRANSLATION = pickle.load(trans_file)
    CROP = pickle.load(crop_file)

    test_model("Gaussian", COLOR_LOOKUP)

