import cv2
import numpy as np

def add_lines(img):

	# convert to binary image to give all areas of tape equal weighting
	b_w = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	b_w = cv2.threshold(b_w, 1, 255, cv2.THRESH_BINARY)[1]

	# wow is this fucking MMAN1300 ???
	try:
		M = cv2.moments(b_w)
		cX = int(M["m10"]/M["m00"])
		cY = int(M["m01"]/M["m00"])
	except:
		cX = 0
		cY = 0
		pass

	# put a cute dot on the centroid
	line = cv2.cvtColor(b_w, cv2.COLOR_GRAY2BGR)
	cv2.circle(line, (cX, cY), 5, (0, 0, 255), -1)

	return line, (cX, cY)