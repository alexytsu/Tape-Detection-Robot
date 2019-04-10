# Import the necessary packages
import time
import numpy as np
import argparse
import cv2
 
# Construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())
 
# Load the image
image = cv2.imread("my_photo-10.jpg")

# Convert BGR to HSV
hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Hardcoded BGR thresholds for colours of interest
BGR_lower_blue = np.uint8([[[45, 17, 0]]])
BGR_upper_blue = np.uint8([[[79, 35, 15]]])

BGR_lower_red = np.uint8([[[20, 12, 51]]])
BGR_upper_red = np.uint8([[[58, 47, 89]]])

BGR_lower_yellow = np.uint8([[[21, 120, 149]]])
BGR_upper_yellow = np.uint8([[[49, 139, 162]]])

#BGR_lower_purple = np.uint8([[[21, 120, 149]]])
#BGR_upper_purple = np.uint8([[[49, 139, 162]]])

# Convert BGR thresholds to HSV
a = cv2.cvtColor(BGR_lower_blue,cv2.COLOR_BGR2HSV)
b = cv2.cvtColor(BGR_upper_blue,cv2.COLOR_BGR2HSV)
aa = cv2.cvtColor(BGR_lower_red,cv2.COLOR_BGR2HSV)
bb = cv2.cvtColor(BGR_upper_red,cv2.COLOR_BGR2HSV)
aaa = cv2.cvtColor(BGR_lower_yellow,cv2.COLOR_BGR2HSV)
bbb = cv2.cvtColor(BGR_upper_yellow,cv2.COLOR_BGR2HSV)
#aaaa = cv2.cvtColor(BGR_lower_purple, cv2.COLOR_BGR2HSV)
#bbbb = cv2.cvtColor(BGR_upper_purple, cv2.COLOR_BGR2HSV)

# Limiting HSV thresholds to H values only
lower_blue = np.array([a[0][0][0]-30,a[0][0][1]-60,a[0][0][2]-60])
upper_blue = np.array([b[0][0][0]+30,b[0][0][1]+60,b[0][0][2]+60])

lower_red = np.array([aa[0][0][0]-10,aa[0][0][1]-50,aa[0][0][2]-50])
upper_red = np.array([bb[0][0][0]+10,bb[0][0][1]+50,bb[0][0][2]+50])

lower_yellow = np.array([aaa[0][0][0]-10,aaa[0][0][1]-50,aaa[0][0][2]-50])
upper_yellow = np.array([bbb[0][0][0]+10,bbb[0][0][1]+50,bbb[0][0][2]+50])

#lower_purple = 
#upper_purple = 

start = time.clock()

# Obtain mask
blueMask = cv2.inRange(hsvImage, lower_blue, upper_blue)
redMask = cv2.inRange(hsvImage, lower_red, upper_red)
yellowMask = cv2.inRange(hsvImage, lower_yellow, upper_yellow)
#purpleMask = cv2.inRange(hsvImage, lower_purple, upper_purple)

end = time.clock()
print (end-start)

# Impose mask over image
HSVblueImage = cv2.bitwise_and(hsvImage, hsvImage, mask = blueMask)
HSVredImage = cv2.bitwise_and(hsvImage, hsvImage, mask = redMask)
HSVyellowImage = cv2.bitwise_and(hsvImage, hsvImage, mask = yellowMask)
#HSVpurpleImage = cv2.bitwise_and(hsvImage, hsvImage, mask = purpleMask)

# Convert the HSV image back to BGR for nicerr viewing
BGRblueImage = cv2.cvtColor(HSVblueImage, cv2.COLOR_BGR2HSV)
BGRredImage = cv2.cvtColor(HSVredImage, cv2.COLOR_BGR2HSV)
BGRyellowImage = cv2.cvtColor(HSVyellowImage, cv2.COLOR_BGR2HSV)

# Display images
cv2.imshow("Resultant Blue", BGRblueImage)
cv2.imshow("Resultant Red", BGRredImage)
cv2.imshow("Resultant Yellow", BGRyellowImage)
#cv2.imshow("Resultant Purple", purpleImage)
cv2.waitKey(0)