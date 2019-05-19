import cv2
import numpy as np
image = cv2.imread("./../images/ipt.jpg")
cv2.imshow("image",image)
pts_src = np.array([[230, 400],[630, 400],[400, 270],[460,270]])
pts_dst = np.array([[230, 400],[630, 400],[230, 250],[630,250]])
h, status = cv2.findHomography(pts_src, pts_dst)
im_out = cv2.warpPerspective(image, h, (image.shape[1],image.shape[0]))
cv2.imshow("image1",im_out)
if cv2.waitKey(0) & 0xFF == ord('q'):
    exit()