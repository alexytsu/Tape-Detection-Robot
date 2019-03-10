import cv2
import numpy as np
import pdb

import line
import arduinointerface

# we want these bounds to be visible to other modules
blue_lower_bounds = np.array([int(69),int(20),int(15)])
blue_upper_bounds = np.array([int(81), int(71), int(80)])

yellow_lower_bounds = np.array([int(0),int(140),int(160)])
yellow_upper_bounds = np.array([int(4), int(160), int(190)])

def mask_tapes(frame):
	# convert to hsv colorspace
	# get the blue tape from the image
	mask_blue = cv2.inRange(frame, blue_lower_bounds, blue_upper_bounds)
	mask_yellow = cv2.inRange(frame, yellow_lower_bounds, yellow_upper_bounds)


	# make the masks compatible with rgb
	mask_rgb_blue = cv2.cvtColor(mask_blue, cv2.COLOR_GRAY2BGR)
	mask_rgb_yellow = cv2.cvtColor(mask_yellow, cv2.COLOR_GRAY2BGR)

	blue_frame = frame & (mask_rgb_blue)
	yellow_frame = frame & (mask_rgb_yellow)
	return blue_frame, yellow_frame

def mask_tape(frame, ser):
	blue, yellow = mask_tapes(frame)

	yellow, y_c = line.add_lines(yellow)
	blue, b_c = line.add_lines(blue)

	both = blue | yellow

	height = both.shape[0]
	width = both.shape[1]

	target = (int((y_c[0] + b_c[0])/2) ,int( (y_c[1] + b_c[1])/2))
	robot = (int(width/2), int(height))

	angle = (115 + 60) / 2
	if(target[0] < width / 2):
		angle = 115
	else:
		angle = 60

	arduinointerface.SendSpeed(ser, angle, 94)

	both = cv2.line(both, robot, target, (0, 255, 0), thickness=4)

	return both


# a dummy function to test the process_video() function
def convert_bw(frame):
	bw_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	bw_frame = cv2.cvtColor(bw_frame, cv2.COLOR_GRAY2BGR)
	return bw_frame


def interactive_mask(frame):

	#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	blue_lower = np.array([150,0,0])
	blue_upper = np.array([255,255,255])

	default = np.array([0,0,0])
	mask_blue = cv2.inRange(frame, blue_lower_bounds, blue_upper_bounds)
	mask_yellow = cv2.inRange(frame, yellow_lower_bounds, yellow_upper_bounds)

	# make the masks compatible with rgb
	mask_rgb_blue = cv2.cvtColor(mask_blue, cv2.COLOR_GRAY2BGR)
	mask_rgb_yellow = cv2.cvtColor(mask_yellow, cv2.COLOR_GRAY2BGR)

	blue_frame = frame & (mask_rgb_blue)
	yellow_frame = frame & (mask_rgb_yellow)
	return blue_frame | yellow_frame
	

def print_pixel(event, x, y, stuff, frame):
	if(event != cv2.EVENT_LBUTTONDOWN):
		return

	print(frame[y][x])



if __name__ == "__main__":
	cap = cv2.VideoCapture(5)

	while True:
		ret, frame = cap.read()

		mask = interactive_mask(frame)
		cv2.imshow('mask', mask)
		cv2.setMouseCallback('mask', print_pixel, frame)


		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()

