import os

import cv2
import pandas as pd
import numpy as np
from skimage import color

from utility import choose_file, basic_video_metrics


def get_spaced_frames(filename, length, get_n):
    """
    From a video get, some evenly space frames
    """

    filepath = os.path.join("footage", filename)
    print(f"From a file of {length} frames we want {get_n} frames")
    spacing = int((length-100)/get_n)
    print("Spacing: ", spacing)

    # initialise loop
    video = cv2.VideoCapture(filepath)
    frames = [] # to be filled
    count = 0   # a simple counter
    n_frames = 0
    success = True # jumpstart the loop
    while success:
        success, image = video.read()
        if count % spacing == 1:
            if image is not None:
                n_frames += 1
                print(f"Grabbed frame {count}/{length}")
                frames.append(image)
                if n_frames >= get_n:
                    print("Grabbed enough")
                    break
        else:
            pass
        count += 1

    print("Finished grabbing on frame:", count)

    return frames, n_frames

class HMI():
    def __init__(self, colour):
        self.n_clicks = 0
        self.pixel_values = []
        self.colour = colour

    def get_pixel_value(self, event, x, y, stuff, frame):
        if(event == cv2.EVENT_LBUTTONDOWN):
            self.n_clicks += 1
            print(self.n_clicks, ":", frame[y][x])
            self.pixel_values.append(frame[y][x])

    def upscale(frame):
        new_frame = cv2.resize(frame, (1920, 1080))
        return new_frame

    def ask_colour_data(self, frame):
        """ 
        From a frame, prod the user to classify some points
        """

        upscaled_frame = HMI.upscale(frame)

        hsv_values = cv2.cvtColor(upscaled_frame, cv2.COLOR_BGR2HSV)

        cv2.imshow("training", upscaled_frame)
        cv2.setMouseCallback("training", self.get_pixel_value, hsv_values)
        cv2.waitKey(0)

        print(f"Saved {self.n_clicks} points of training data for {self.colour}")
        return self.pixel_values

def gap():
    print("\n______________________________")

def collect_points(filename=None):
    print("===== PLANNER APP: pick some points for the classifier to read =====")
    if filename is None:
        filename = choose_file("footage")

    video_name = os.path.splitext(filename)[0] 
    print("Selected:", filename) 

    try:
        os.mkdir(os.path.join("training_data", video_name))
    except FileExistsError:
        response =  input("Data already exists. Would you like to repick? (y/n)")
        if response == 'y':
            pass
        else:
            return

    # show some basic metrics about the video
    gap()
    print("Metrics: ", filename)
    w, h, l, f = basic_video_metrics(filename)
    print("width: ", w)
    print("height: ", h)
    print("length: ", l)
    print("fps: ", f)
    print("duration (s): ", round(l/f, 2))

    # get some evenly space frames from the video
    gap()
    get_n = 5
    frames, n_got = get_spaced_frames(filename, l, get_n)
    print(f"Tried to get {get_n} frames and got {n_got}")

    # for each frame ask for blue points, yellow points and ground points
    gap()
    for colour in ["blue", "red", "yellow", "other", "green"]:
        Classifier = HMI(colour)
        total_data = pd.DataFrame()

        for frame in frames:
            print("Click on points that are ", colour)
            data_points = Classifier.ask_colour_data(frame)
            data_matrix = np.array(data_points)

            try:

                df = pd.DataFrame({
                    "H": data_matrix[:,0],
                    "S": data_matrix[:,1],
                    "V": data_matrix[:,2]
                })

                total_data = total_data.append(df)

            except IndexError:
                print("You didn't select any points")

        filename = colour + ".csv"
        filepath = os.path.join("training_data", video_name, filename)
        total_data.to_csv(filepath)

if __name__ == "__main__":
    collect_points()
