import cv2
import numpy as np
import pickle 

pts_src = np.array([[174, 377],[301, 44],[545, 51],[659,379]])
pts_dst = np.array([[174, 377],[174, 0],[659, 0],[659,379]])

counter = 0

def readmouse(event,x,y,flags,param):
	global counter
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print (x,y)
		print(pts_src[counter][0])
		print(pts_src[counter][1])
		pts_src[counter][0] = x;
		pts_src[counter][1] = y;
		counter+=1

camera = input("input camera: ")
cam = cv2.VideoCapture(int(camera))
print("[0] re-tune matrix \n[1] reload old matrix")

val = input()
if(val == 1):
	cv2.namedWindow('image')
	cv2.setMouseCallback('image',readmouse)
	while(counter < 4):
		ret_val, image = cam.read()
		cv2.imshow("image",image)
		k = cv2.waitKey(1) & 0xFF
		if k == ord('b'):
			break
	print(pts_src);
	x1 = pts_src[1][0] 
	x2 = pts_src[2][0] 
	y1 = 0#pts_src[0][1] 
	y2 = pts_src[2][1]
	pts_dst = np.array([[x1, y1],[x1, y2],[x2, y2],[x2,y1]])
	cv2.destroyAllWindows()
	h, status = cv2.findHomography(pts_src, pts_dst)
	pickle.dump( h, open( "homographyMatrix.p", "wb" ))


h = pickle.load( open( "homographyMatrix.p", "rb" ))
h[0][2] = 0
h[1][2] = 0
print(h)
while True:
	ret_val, image = cam.read()
	img = cv2.warpPerspective(image, h, (2*image.shape[1],image.shape[0]))
	cv2.imshow('my webcam', img)
	if cv2.waitKey(1) == 27: 
		break  # esc to quit

cv2.destroyAllWindows()