import argparse
from threading import Thread
import time

import cv2

from arduino import getSerialPort, SendSpeed
from vision import get_color_lookup, get_perspective_warp, WebcamVideoStream, applyIPT, mask_lookup, get_edges
from nav import plan_steering
from car import Car

ARGS = None


def run(video, arduino, color_lookup, mapping, translation, crop, crop_other, car):

    prev_frame = 0
    lastRealFrame = time.time()

    tape_count = 0
    frames = 0
    while True:
        # ============= DECODE THE VIDEO FRAME
        start_time = time.time()
        frame, frame_n = video.read()

        if prev_frame == frame_n:
            continue
        else:
            if ARGS.debug_text:
                gap = time.time() - lastRealFrame
                lastRealFrame = time.time()
                print(f"Frame Gap: {1/(gap):.2f} FPS {gap*1000:.2f} ms")

        prev_frame = frame_n
        if frame is None:
            print("Pass")
            continue

        # ============= RESIZE AND FLATTEN THE FRAME
        frame = cv2.resize(frame, (480, 360), interpolation = cv2.INTER_AREA)
        tape_frame = applyIPT(frame, mapping, translation, crop)

        # ============= CLASSIFY THE COLORS
        colors = mask_lookup(tape_frame, color_lookup)

        # ============= MAKE A STEERING DECISION
        angle, speed, saw_tape = plan_steering(colors, tape_frame, ARGS.show_camera)
        frames += 1
        print(frames)
        if saw_tape:
            if frames < 900:
                threshold = 3
            else:
                threshold = 3
            tape_count += 2
            if tape_count >= threshold:
                stop_frame = frames + 20
        else:
            tape_count -= 1
            tape_count = max(0, tape_count)


        # ============= CONTROL THE CAR
        CAR.SendSteering(int(angle))
        send_speed = 10
        TURBO_SPEED = 70
        NORMAL_SPEED = 50
        TURNING_SPEED = 35
        OBSTACLE_SPEED = 25

        if speed == 0:
            send_speed = OBSTACLE_SPEED
        elif speed == 1:
            send_speed = TURNING_SPEED
        elif speed == 2:
            send_speed = NORMAL_SPEED
        elif speed == 3:
            send_speed = TURBO_SPEED

        if saw_tape:
            send_speed = TURNING_SPEED

        if frames < 20:
            send_speed = 90

        CAR.SendThrottle(send_speed)

        # ============ PRINT DEBUGGING INFORMATION
        end_time = time.time()
        if ARGS.debug_text:
            print(f"Processing FPS: {1/(end_time - start_time):.2f}")



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
        CAR.Sync()
    except Exception as e:
        print(e)
        CAR = None
        exit()

    COLOR_LOOKUP = get_color_lookup() # load the trained color table
    MAPPING, TRANSLATION, CROP, CROP_OTHER = get_perspective_warp() # load the camera transforms
    STREAM = WebcamVideoStream(ARGS.camera).start()
    print("Initialised all")
    input("press enter to start:")
    run(STREAM, SER, COLOR_LOOKUP, MAPPING, TRANSLATION, CROP, CROP_OTHER, CAR)
    # Thread(target=run, args=(STREAM, SER, COLOR_LOOKUP, MAPPING, TRANSLATION, CROP,CROP_OTHER,CAR)).start()

