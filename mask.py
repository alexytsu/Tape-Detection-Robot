import cv2
import numpy as np

import line

# we want these bounds to be visible to other modules
blue_lower_bounds = np.array([int(174/2),int(255*.38),int(255*.58)])
blue_upper_bounds = np.array([int(250/2), 255, 255])
yellow_lower_bounds = np.array([int(40/2),int(255*.38),int(255*.58)])
yellow_upper_bounds = np.array([int(70/2), 255, 255])

def mask_tapes(frame):
	# convert to hsv colorspace
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	# get the blue tape from the image
	mask_blue = cv2.inRange(frame, blue_lower_bounds, blue_upper_bounds)
	mask_yellow = cv2.inRange(frame, yellow_lower_bounds, yellow_upper_bounds)

	# make the masks compatible with rgb
	mask_rgb_blue = cv2.cvtColor(mask_blue, cv2.COLOR_GRAY2BGR)
	mask_rgb_yellow = cv2.cvtColor(mask_yellow, cv2.COLOR_GRAY2BGR)

	blue_frame = frame & (mask_rgb_blue)
	yellow_frame = frame & (mask_rgb_yellow)
	return blue_frame, yellow_frame

def mask_tape(frame):
	# get the separate blue and yellow channels
	blue, yellow = mask_tapes(frame)

	# get the masks and centroid coordinates for each tape
	yellow, y_c = line.add_lines(yellow)
	blue, b_c = line.add_lines(blue)

	# combine the mask
	both = blue | yellow

	# kms
	height = both.shape[0]
	width = both.shape[1]

	# calculate a target vector as the average of the two centroids
	target = (int((y_c[0] + b_c[0])/2) ,int( (y_c[1] + b_c[1])/2))
	robot = (int(width/2), int(height))

	# graph the target vector for stupid humans to "visualize" god fuck
	both = cv2.line(both, robot, target, (0, 255, 0), thickness=4)

	return both


# a dummy function to test the process_video() function
def convert_bw(frame):
	bw_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	bw_frame = cv2.cvtColor(bw_frame, cv2.COLOR_GRAY2BGR)
	return bw_frame
