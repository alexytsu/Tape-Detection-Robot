import os

import cv2
import pandas as pd
import numpy as np

from skimage import color

def choose_file():
    """
    Let the user choose the file they wish to work on
    """
    
    # List all the video files we have 
    video_files = os.listdir("footage")
    n_files = len(video_files)
    for idx, video in enumerate(video_files):
        print(f"[{idx}]: {video}")

    file_n = input(f"Select the video file (0-{n_files-1}): ")
    try:
        file_n = int(file_n)
        if(file_n >= n_files):
            print("Invalid file index chosen")
            exit()
    except:
        print("Invalid file selection")
        exit()
    
    filename = video_files[file_n]
    return filename

def basic_video_metrics(filename):
    """
    Get the height, width, fps and length of the footage
    """
    filepath = os.path.join("footage", filename)
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise Exception("No footage found: ", filepath)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    return width, height, length, fps

def get_spaced_frames(filename, length, get_n):
    """
    From a video get, some evenly space frames
    """

    filepath = os.path.join("footage", filename)
    print(f"From a file of {length} frames we want {get_n} frames")
    spacing = int((length-1)/get_n)
    print("Spacing: ", spacing)

    # initialise loop
    video = cv2.VideoCapture(filepath)
    frames = [] # to be filled
    count = 0   # a simple counter
    n_frames = 0
    success = True # jumpstart the loop
    while success:
        success, image = video.read()
        if(success):
            if count % spacing == 0:
                n_frames += 1
                print(f"Grabbed frame {count}/{length}")
                frames.append(image)
                if n_frames >= get_n:
                    break
        else:
            break
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

if __name__ == "__main__":
    print("===== PLANNER APP: pick some points for the classifier to read =====")
    filename = choose_file()
    print("Selected:", filename) 

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
    get_n = 4
    frames, n_got = get_spaced_frames(filename, l, get_n)
    print(f"Tried to get {get_n} frames and got {n_got}")

    # for each frame ask for blue points, yellow points and ground points
    gap()
    for colour in ["blue", "red", "yellow"]:
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
        filepath = os.path.join("training_data", filename)
        total_data.to_csv(filepath)


