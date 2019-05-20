import os
import pickle
import argparse
import pdb
import sys

import cv2
import numpy as np
from matplotlib import pyplot as plt

from utility import choose_file
from fr import PyFrame

DEBUG = True
CAMERA = True

def mask_image(image, model, frame_n):

    if DEBUG:
        print("Analysing frame", frame_n)

    # Convert BGR to HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    H = hsvImage[:,:,0]
    S = hsvImage[:,:,1]

    # find how long the one dimensional form needs to be
    one_dim_length = hsvImage.shape[0] * hsvImage.shape[1]
    # now spread out the image [HSV]
    Xnew = np.reshape(hsvImage, (one_dim_length, 3))
    # only take H and S
    Xnew = Xnew[:,0:2]

    return model.predict(Xnew)
    
def show_masks(ynew, image):
    roi = np.where(ynew == 1)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (0, 200, 100)

    roi = np.where(ynew == 3)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (200, 200, 100)


    roi = np.where(ynew == 4)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (0, 0, 0)


    image = cv2.resize(image, (1280, 720))
    cv2.imshow('res', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit()

def plan_steering(classified, image):
    height = image.shape[0]
    width = image.shape[1]
    """
    opencv_image = np.array(classified * 50, dtype = np.uint8)
    opencv_image = np.array([(0,x,0) for x in opencv_image], dtype=np.uint8)
    opencv_image = np.array(opencv_image, dtype = np.uint8)
    opencv_image = np.reshape(opencv_image, (height, width, 3))

    gray = cv2.cvtColor(opencv_image,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    cv2.imshow('canny', edges)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        exit()

    minLineLength = 0
    maxLineGap = 10


    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(opencv_image,(x1,y1),(x2,y2),(255,0,0),2)



    cv2.imshow('hough', opencv_image)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        exit()
    """


    imagified = np.reshape(classified, (height, width))
    c_array = imagified / 5
    cFrame = PyFrame(c_array)

    pointList = cFrame.getTapePoints()
    for point in pointList:
        x, y = point
        try:
            cv2.circle(image, (x, y), 3, (0,0,255), 1)
        except:
            print("failed")
            pass

    pointList = cFrame.getMidPoints()
    for point in pointList:
        x, y = point
        try:
            cv2.circle(image, (x, y), 3, (0,255,0), 1)
        except:
            print("failed")
            pass

    lineList = cFrame.getBlueLine()
    for line in lineList:
        print(line)
        end, start = line
        x1, y1 = end;
        x2, y2 = start;
        cv2.line(image, (x1,y1), (x2,y2), (255,0,0), 2)

    lineList = cFrame.getYellowLine()
    for line in lineList:
        print(line)
        end, start = line
        x1, y1 = end;
        x2, y2 = start;
        cv2.line(image, (x1,y1), (x2,y2), (0,255,255), 2)

    lineList = cFrame.getNavLine()
    for line in lineList:
        print(line)
        end, start = line
        x1, y1 = end;
        x2, y2 = start;
        cv2.line(image, (x1,y1), (x2,y2), (0,255,0), 2)

    cv2.imshow('res', cv2.resize(image, (1280, 720)))
    if(CAMERA):
        cv2.waitKey(1)
    else:
        if cv2.waitKey(0) & 0xFF == ord('q'):
            exit()



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

        small = cv2.resize(frame, (256, 144))
        ynew = mask_image(small, model, frame_n)
        plan_steering(ynew, small)
        frame_n += 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Running with CAMERA mode on by default")
        print("Use 'python tester.py --test' to use a saved video")
    else:
        if sys.argv[1] == '--test':
            CAMERA = False
    test_model("Adaboost")