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

DEBUG = True
CAMERA = True
SER = None

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

    lateral_error = 0
    pointList = cFrame.getMidPoints()
    for point in pointList:
        x, y = point
        try:
            cv2.circle(image, (x, y), 3, (0,255,0), 1)
            lateral_error += x - width/2 
        except:
            print("failed")
            pass
    try:    
        lateral_error = lateral_error/len(pointList)
    except:
        pass

    blueLine = None
    yellowLine = None
    navLine = None

    lineList = cFrame.getBlueLine()
    for line in lineList:
        end, start = line
        x1, y1 = end;
        x2, y2 = start;
        cv2.line(image, (x1,y1), (x2,y2), (255,0,0), 1)
        blueLine = line

    lineList = cFrame.getYellowLine()
    for line in lineList:
        end, start = line
        x1, y1 = end;
        x2, y2 = start;
        cv2.line(image, (x1,y1), (x2,y2), (0,255,255), 1)
        yellowLine = line

    lineList = cFrame.getNavLine()
    for line in lineList:
        end, start = line
        x1, y1 = start;
        x2, y2 = end;
        cv2.line(image, (x1,y1), (x2,y2), (0,255,0), 2)
        navLine = line

    def getLineAttributes(line):
        end, start = line
        x1, y1 = start;
        x2, y2 = end;
        angle_hor = x2 - x1
        angle_ver = y1 - y2
        angle_error = math.degrees(math.atan2(angle_hor, angle_ver))
        I = 0.5
        P = 0.2
        steering_angle = I * lateral_error + P * angle_error
        return lateral_error, angle_error, steering_angle
    
    def writeLineAttributes(lat, angle, steer, image):
        cv2.putText(image, f'Lateral Error: {lat:.2f}', (10, 15), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0), 1, cv2.LINE_AA)
        cv2.putText(image, f'Angular Error: {angle:.2f}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0), 1, cv2.LINE_AA)
        cv2.putText(image, f'Steering Angle: {steer:.2f}', (10, 45), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0), 1, cv2.LINE_AA)


    if navLine is not None:
        print("nav")
        print(navLine)
        lat, angle, steer = getLineAttributes(navLine)
        writeLineAttributes(lat, angle, steer, image)
        return angle
    elif blueLine and yellowLine:
        print("blue + yellow")
        lat1, angle1, steer1 = getLineAttributes(blueLine)
        lat2, angle2, steer2 = getLineAttributes(yellowLine)
        lat = (lat1 + lat2) / 2
        angle = (angle1 + angle2) / 2
        steer = (steer1 + steer2) / 2
        writeLineAttributes(lat, angle, steer, image)
        return angle
    elif blueLine:
        print("blue")
        lat, angle, steer = getLineAttributes(blueLine)
        writeLineAttributes(lat, angle, steer, image)
        return angle
    elif yellowLine:
        print("yellow")
        lat, angle, steer = getLineAttributes(yellowLine)
        writeLineAttributes(lat, angle, steer, image)
        return angle

    cv2.imshow('res', cv2.resize(image, (1280, 720)))
    if(CAMERA):
        cv2.waitKey(1)
    else:
        if cv2.waitKey(0) & 0xFF == ord('q'):
            exit()


def applyIPT(image):
    pts_src = np.array([[174, 377],[301, 44],[545, 51],[659,379]])
    pts_dst = np.array([[174, 377],[174, 0],[659, 0],[659,379]])
    h, status = cv2.findHomography(pts_src, pts_dst)
    im_out  = cv2.warpPerspective(image, h, (image.shape[1],image.shape[0]))

    return im_out


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

        small = cv2.resize(frame, (256, 144))
        ynew = mask_image(small, model, frame_n)
        angle = plan_steering(ynew, small)
        SendSpeed(SER, angle, 90)

        frame_n += 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Running with CAMERA mode on by default")
        print("Use 'python tester.py --test' to use a saved video")
    else:
        if sys.argv[1] == '--test':
            CAMERA = False
    SER = getSerialPort()
    test_model("Adaboost")