""" 
Takes a video file or camera stream and allows our modules to run on it frame by frame
"""

import numpy as np 
import cv2
import os
import time

import mask

CUR_DIR = os.path.dirname(__file__)
VIDEO_FILE = os.path.join(CUR_DIR, 'footage/test1.mp4')


def process_video(video, process):
	"""
	Using a pipe and filter philosophy, this module allows the user to run a function on each frame of the video being streamed
	"""

	print("Starting streaming video...")

	# Open the video for streaming frame-by-frame
	cap = cv2.VideoCapture(video)
	curtime = 0
	while cap.isOpened():

		oldtime = curtime
		curtime = int(round(time.time() * 1000))	
		delta = curtime - oldtime
		print("time: ", delta, "hz: ", (1/delta)*1000)

		ret, frame = cap.read()

		# Process each frame of the video
		mutated = process(frame)

		# Show the original and processed frame side by side
		"""
		comparison = np.hstack((frame, mutated))
		cv2.imshow('comparison', comparison)
		"""

		#Show only the processed from
		#cv2.imshow('processed', mutated)

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

	# run the process with bw demo
	process_video(VIDEO_FILE, mask.mask_tape)
