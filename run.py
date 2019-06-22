import argparse
from threading import Thread
import time

import cv2

from arduino import getSerialPort, SendSpeed
from vision import get_color_lookup, get_perspective_warp, WebcamVideoStream, applyIPT, mask_lookup, get_edges
from nav import plan_steering
from car import Car

ARGS = None

def run(video, arduino, color_lookup, mapping, translation, crop, car):
    prev_frame = 0
    while True:
        start_time = time.time()
        frame, frame_n = video.read()

        if prev_frame == frame_n:
            continue

        prev_frame = frame_n
        if frame is None:
            print("Pass")
            continue
        frame = cv2.resize(frame, (320, 240), interpolation = cv2.INTER_AREA)
        tape_frame = applyIPT(frame, mapping, translation, crop)
        
        # resize the navigation frame
        """
        w = 100
        h = 100
        tape_frame = cv2.resize(tape_frame, (w, h))
        """
    
        # preprocess
        """
        tape_edges = get_edges(tape_frame, ARGS.debug_camera) 
        tape_edges = cv2.cvtColor(tape_edges, cv2.COLOR_GRAY2BGR)
        tape_frame = tape_edges & tape_frame
        """

        # classify
        colors = mask_lookup(tape_frame, color_lookup)

        # analyse tape and get a steering direction
        angle, speed = plan_steering(colors, tape_frame, ARGS.show_camera)
        ## SendSpeed(arduino, int(angle), speed)
        CAR.SendThrottle(26300)
        CAR.SendSteering(int(angle))


        end_time = time.time()
        if ARGS.debug_text:
            print(f"FPS: {1/(end_time - start_time):.2f}")



if __name__ == "__main__":

    # Collect some options from the user
    parser = argparse.ArgumentParser(description="Run the robot")
    # Don't show camera by default
    parser.add_argument('--debug', action='store_const', const=True, default=False, help="Turn on all other debugging flags") 
    parser.add_argument('--show-camera', action='store_const', const=True, default=False, help="Shows live feeds for debugging") 
    parser.add_argument('--debug-camera', action='store_const', const=True, default=False, help="Shows detailed feeds for debugging") 
    parser.add_argument('--debug-text', action='store_const', const=True, default=False, help="Shows some sparse information for debugging") 
    parser.add_argument('--camera', default=0, help="Choose which camera to work off", type=int) 
    ARGS = parser.parse_args()

    if ARGS.debug:
        ARGS.debug_camera = True
        ARGS.debug_text = True
        ARGS.show_camera = True

    # Initialise the necessary hardware and AI
    SER = None
    try:
        SER = getSerialPort() # open port to Arduino controller
    except:
        SER = None

    try:
        CAR = Car()
        CAR.sync()
    except:
        CAR = None

    COLOR_LOOKUP = get_color_lookup() # load the trained color table
    MAPPING, TRANSLATION, CROP = get_perspective_warp() # load the camera transforms
    STREAM = WebcamVideoStream(ARGS.camera).start()
    print("Initialised all")
    run(STREAM, SER, COLOR_LOOKUP, MAPPING, TRANSLATION, CROP, CAR)
    # Thread(target=run, args=(STREAM, None, COLOR_LOOKUP, MAPPING, TRANSLATION, CROP,)).start()

