import argparse
from threading import Thread

from arduino import getSerialPort, SendSpeed
from vision import get_color_lookup, get_perspective_warp, WebcamVideoStream, applyIPT, mask_lookup
from nav import plan_steering

def run(video, arduino, color_lookup, mapping, translation, crop):
    while True:
        frame = video.read()
        tape_frame = applyIPT(frame)
        
        # resize the navigation frame
        w = 300
        h = 300
        tape_frame = cv2.resize(tape_frame)
    
        # preprocess
        tape_edges = get_edges(tape_frame) 
        tape_edges = cv2.cvtColor(tape_edges, cv2.COLOR_GRAY2BGR)
        tape_frame = tape_edges & tape_frame

        # classify
        colors = mask_lookup(frame, color_lookup)

        # analyse tape and get a steering direction
        angle, speed = plan_steering(colors, tape_frame)
        SendSpeed(arduino, int(angle), speed)


if __name__ == "__main__":

    # Collect some options from the user
    parser = argparse.ArgumentParser(description="Run the robot")
    # Don't show camera by default
    parser.add_argument('--show-camera', action='store_const', const=True, default=False, help="Shows live feeds for debugging") 
    parser.add_argument('--debug-camera', action='store_const', const=True, default=False, help="Shows detailed feeds for debugging") 
    args = parser.parse_args()

    SHOW_CAMERA = args.show_camera
    DEBUG_CAMERA = args.debug_camera

    # Initialise the necessary hardware and AI
    SER = getSerialPort() # open port to Arduino controller
    COLOR_LOOKUP = get_color_lookup() # load the trained color table
    MAPPING, TRANSLATION, CROP = get_perspective_warp() # load the camera transforms
    STREAM = WebcamVideoStream(0)
    Thread(target=run args=[STREAM, SER, COLOR_LOOKUP, MAPPING, TRANSLATION, CROP]).start()

