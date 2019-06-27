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
from nav import plan_steering, getLineAttributes, AngleBuffer
from vision import applyIPT, get_edges, mask_lookup, WebcamVideoStream
from trainer import create_lookup, train_classifier
from planner import collect_points

DEBUG = True
SER = None
MAPPING = None
TRANSLATION = None
CROP = None
CAMERA = True

go = 95


def test_model(color_table, filename=None):

    # load the video file
    if CAMERA:
        video = WebcamVideoStream(src=5).start()
    else:
        """
        video_file_path = os.path.join("footage", choose_file("footage"))
        video = cv2.VideoCapture(video_file_path)
        """
        video = cv2.VideoCapture(os.path.join("footage", filename))

    frame_n = 0
    smoother = AngleBuffer(1)
    while True:
        frame = None
        if CAMERA:
            frame, thread_frame_number = video.read()
            #frame = applyIPT(frame, MAPPING, TRANSLATION, CROP)
        else:
            retval, frame = video.read()
            if not retval:
                pass
                

        # resize
        w = 200
        h = 200
        frame = cv2.resize(frame, (w, h))
        frame = frame[0:int(h/2), 0:w]
        frame = cv2.resize(frame, (w, h))
        original = np.copy(frame)

        # preprocess
        edges = get_edges(frame, True)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        # frame = edges & frame

        full_ynew = mask_lookup(frame, color_table)
        mask_image = show_masks(full_ynew, frame, "full", w, h)

        horizontal1 = np.concatenate((original, mask_image), axis=1)
        horizontal2 = np.concatenate((edges, frame), axis=1)
        total = np.concatenate((horizontal1, horizontal2), axis=0)

        cv2.imshow("debug", total)

        # classify
        other_ynew = mask_lookup(frame, color_table)

        angle,speed = plan_steering(other_ynew, frame, None, None, True)

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


    ipm_file = open('../IPMtest/source/homographyMatrix.p', 'rb')
    trans_file = open('../IPMtest/source/Translation.p', 'rb')
    crop_file = open('../IPMtest/source/Crop.p', 'rb')
    MAPPING = pickle.load(ipm_file)
    TRANSLATION = pickle.load(trans_file)
    CROP = pickle.load(crop_file)

    print("Data Foldername: ")
    video_filename = choose_file("footage")
    video_file_path = os.path.join("footage", video_filename)
    video_name = os.path.splitext(video_filename)[0]
    classifier = input("Classifier to test: ")
    potential_lookup = os.path.join("trained_models", video_name, classifier+"_lookup.sav")
    exists = os.path.isfile(potential_lookup)
    
    if exists:
        print("Using existing classifier")
    else:
        collect_points(video_filename)
        model = train_classifier(video_name, classifier)
        create_lookup(classifier, video_name, model)

    lookup_file = open(potential_lookup, "rb")
    COLOR_LOOKUP = pickle.load(lookup_file)
    test_model(COLOR_LOOKUP, video_filename)
