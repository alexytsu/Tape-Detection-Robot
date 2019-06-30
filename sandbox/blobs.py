import math

import cv2
import numpy as np

image = cv2.imread('blob3.png')
bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def get_box_ratio(box):
    a, b, c, d = box
    a1, a2 = a
    b1, b2 = b
    c1, c2 = c
    dist_1 = math.sqrt((a1 - b1) ** 2 + (a2 - b2) ** 2 )
    dist_2 = math.sqrt((c1 - b1) ** 2 + (c2 - b2) ** 2 )
    return max(dist_1/dist_2, dist_2/dist_1)

contours, _ = cv2.findContours(bw, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
rectangles = list(map(cv2.minAreaRect, contours))
boxes = list(map(cv2.boxPoints, rectangles))
boxes = list(map(np.int0, boxes))
boxes = sorted(boxes, key=get_box_ratio, reverse=True)

for box in boxes:
    cv2.drawContours(image, [box], 0, (0, 0, 200), 2)
    break

cv2.imshow("hi", image)
cv2.waitKey(0)