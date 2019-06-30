
import argparse
from threading import Thread
import time

import cv2

from arduino import getSerialPort, SendSpeed
from vision import get_color_lookup, get_perspective_warp, WebcamVideoStream, applyIPT, mask_lookup, get_edges
from nav import plan_steering
from car import Car


video = WebcamVideoStream(4).start()

while True:
    prev_frame = 0
    lastRealFrame = time.time()
    while True:

        start_time = time.time()
        frame, frame_n = video.read()

        if prev_frame == frame_n:
            time.sleep(0.005)
            continue
        else:
            gap = time.time() - lastRealFrame
            lastRealFrame = time.time()
            print(f"{1/(gap):.2f} FPS {gap*1000:.2f} ms")

        prev_frame = frame_n
        if frame is None:
            print("Pass")
            continue

