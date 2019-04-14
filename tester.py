import os
import pickle
import argparse
import pdb

import cv2
import numpy as np

from utility import choose_file

def mask_image(image, model, frame_n):

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

def test_model(model_name):

    # load the model
    model_file_path = os.path.join("trained_models", model_name, "model.sav")
    model_file = open(model_file_path, "rb")
    model = pickle.load(model_file)

    # load the video file
    video_file_path = os.path.join("footage", choose_file())
    video = cv2.VideoCapture(video_file_path)
    frame_n = 0
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            print("Video finished")
            break

        small = frame
        ynew = mask_image(small, model, frame_n)
        if(frame_n % 30 == 0):
            show_masks(ynew, small)
        frame_n += 1

    


if __name__ == "__main__":
    test_model("Adaboost")
