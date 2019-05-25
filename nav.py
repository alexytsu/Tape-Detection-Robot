import math

import cv2
import numpy as np

from fr import PyFrame
from helper import writeLineAttributes
SHOW_CAMERA = False
CAMERA = False

def getLineAttributes(line):
    lateral_error = 0
    end, start = line
    x1, y1 = start
    x2, y2 = end
    angle_hor = x2 - x1
    angle_ver = y1 - y2
    angle_error = math.degrees(math.atan2(angle_hor, angle_ver))
    I = 0.3
    P = 0.4
    steering_angle = I * lateral_error + P * angle_error
    return lateral_error, angle_error, steering_angle


def plan_steering(classified, image):
    height = image.shape[0]
    width = image.shape[1]

    imagified = np.reshape(classified, (height, width))
    c_array = imagified / 5
    cFrame = PyFrame(c_array)

    pointList = cFrame.getTapePoints()

    lateral_error = 0
    pointList = cFrame.getMidPoints()
    for point in pointList:
        try:
            x, y = point
            lateral_error += x - width / 2
            cv2.circle(image, (x, y), 2, (0, 100, 0), 1)
        except:
            pass

    try:
        lateral_error = lateral_error / len(pointList)
    except:
        print("No Points")

    pointList = cFrame.getDarkPoints()
    for point in pointList:
        x, y = point
        try:
            cv2.circle(image, (x, y), 2, (255, 100, 100), 1)
        except:
            print("Failed")

    blank_image = np.zeros((height,width), np.uint8)
    for point in pointList:
        x, y = point
        blank_image[y][x] = 255

    lines = cv2.HoughLines(blank_image, 4, np.pi / 180, 100, None, 0, 0)
    print(lines)
    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            image = cv2.line(image, pt1, pt2, (255), 1, cv2.LINE_AA)

    pointList = cFrame.getLightPoints()
    for point in pointList:
        x, y = point
        try:
            cv2.circle(image, (x, y), 2, (0, 100, 100), 1)
        except:
            print("Failed")


    """
    cv2.imshow("image", cv2.resize(image, (1280,720)))
    cv2.imshow("houghPre", blank_image)
    if cv2.waitKey(0) & 0xFF == ord("q"):
        exit()
    """

    blueLine = None
    yellowLine = None
    navLine = None

    lineList = cFrame.getBlueLine()
    for line in lineList:
        end, start = line
        x1, y1 = end
        x2, y2 = start
        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 1)
        blueLine = line

    lineList = cFrame.getYellowLine()
    for line in lineList:
        end, start = line
        x1, y1 = end
        x2, y2 = start
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 255), 1)
        yellowLine = line

    lineList = cFrame.getNavLine()
    for line in lineList:
        end, start = line
        x1, y1 = start
        x2, y2 = end
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        navLine = line


    retval = 0

    if navLine is not None:
        print("nav")
        lat, angle, steer = getLineAttributes(navLine)
        writeLineAttributes(lat, angle, steer, image)
        retval = steer
    elif blueLine and yellowLine:
        print("blue + yellow")
        lat1, angle1, steer1 = getLineAttributes(blueLine)
        lat2, angle2, steer2 = getLineAttributes(yellowLine)
        lat = (lat1 + lat2) / 2
        angle = (angle1 + angle2) / 2
        steer = (steer1 + steer2) / 2
        writeLineAttributes(lat, angle, steer, image)
        retval = steer
    elif blueLine:
        print("blue")
        lat, angle, steer = getLineAttributes(blueLine)
        writeLineAttributes(lat, angle, steer, image)
        retval = 2.5 * steer
    elif yellowLine:
        print("yellow")
        lat, angle, steer = getLineAttributes(yellowLine)
        writeLineAttributes(lat, angle, steer, image)
        retval = 2.5 * steer

    if SHOW_CAMERA:
        cv2.imshow("res", cv2.resize(image, (1280, 720)))
        if CAMERA:
            cv2.waitKey(1)
        else:
            if cv2.waitKey(0) & 0xFF == ord("q"):
                exit()
    return retval