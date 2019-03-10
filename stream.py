""" 
Takes a video file or camera stream and allows our modules to run on it frame by frame
"""

import numpy as np 
import cv2
import os

import serial

import mask

CUR_DIR = os.path.dirname(__file__)
VIDEO_FILE = os.path.join(CUR_DIR, 'footage/test1.mp4')


def process_video(video, process):
	"""
	Using a pipe and filter philosophy, this module allows the user to run a function on each frame of the video being streamed
	"""

	print(f"Starting streaming {video}...")

	ser = serial.open("/dev/tty/ACM0")

	# Open the video for streaming frame-by-frame
	cap = cv2.VideoCapture(video)
	while cap.isOpened():
		ret, frame = cap.read()

		# Process each frame of the video
		mutated = process(frame, ser)

		# Show the original and processed frame side by side
		comparison = np.hstack((frame, mutated))
		cv2.imshow('comparison', comparison)

		# use p to pause
		if cv2.waitKey(1) & 0xFF == ord('p'):
			while True:
				if cv2.waitKey(1) & 0xFF == ord('p'):
					break

		# Poll for user quit
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()
	print("Closing video stream")


if __name__ == "__main__":
	

	filename = input("Filename: ")
	# run the process with bw demo
	try:
		process_video(filename, mask.mask_tape)
	except:
		print("Terminating early")	
	finally:
		print("Exiting...")