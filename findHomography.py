import cv2
import numpy as np

vertical_warp = 0
horizontal_warp = 0

camera = input("input camera: ")
cam = cv2.VideoCapture(int(camera))

while True:
    ret_val, image = cam.read()
    vert_input = input("Vertical warp")
    hor_input = input("Horizontal warp")

    if vert_input:
        vertical_warp = int(vert_input)
    if hor_input:
        horizontal_warp = int(hor_input)


    print(f"{vertical_warp}.{horizontal_warp}")
    pts_src = np.array([[0,0],[100,0],[0,100],[100,100]])
    pts_dst = np.array([[0,0],[100,0],[50-horizontal_warp,100+vertical_warp],[50+horizontal_warp, 100+vertical_warp]])
    print(pts_dst)
    print(pts_src)

    h, status = cv2.findHomography(pts_src, pts_dst)
    img = cv2.warpPerspective(image, h, (image.shape[1],image.shape[0]))
    cv2.imshow('my webcam', img)
    if cv2.waitKey(1) == 27: 
        break  # esc to quit
