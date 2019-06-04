import math

import cv2
import numpy as np

from fr import PyFrame
from helper import writeLineAttributes

SHOW_CAMERA = True
CAMERA = True

def gradientIntercept(line, height):
    start, end = line
    x1, y1 = start
    x2, y2 = end
    y1 = height - y1
    y2 = height - y2
    start = (x1, y1)
    end = (x2, y2)
    # m, b = np.polyfit(start, end, 1)


def getLineAttributes(line, width, height):
    lateral_error = 0
    end, start = line
    gradientIntercept(line, height)
    x1, y1 = start
    x2, y2 = end

    if y1 < y2:
        x1, y1, x2, y2 = x2, y2, x1, y1

    angle_hor = x2 - x1
    angle_ver = y1 - y2
    angle_error = math.degrees(math.atan2(angle_hor, angle_ver))

    return angle_error

def analyseLineScatter(image, pointList, height, width):
    blank_image = np.zeros((height, width), np.uint8)
    xy_sum = 0
    y_sum = 0
    for point in pointList:
        x, y = point
        blank_image[y][x] = 255
        xy_sum = xy_sum + x * y
        y_sum = y_sum + y

    x_avg = width/2
    try:
        x_avg = xy_sum / y_sum
    except:
        pass

    houghLines = []
    lines = cv2.HoughLines(blank_image, 4, np.pi / 50, 30, None, 0, 0)
    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            pt1 = (x1, y1)
            pt2 = (x2, y2)
            houghLines.append((pt2, pt1))
            image = cv2.line(image, pt1, pt2, (255, 255, 255), 1, cv2.LINE_AA)

    houghAngles = []
    for line in houghLines:
        angle = getLineAttributes(line, width, height)
        houghAngles.append(angle)

    try:
        angle = sum(houghAngles)/len(houghAngles)
        angle = int(angle)
        return angle, int(x_avg - width/2)
    except Exception as e:
        return None, int(x_avg - width/2)


def plot_pointlist(image, pointList, color):
    for point in pointList:
        try:
            x, y = point
            cv2.circle(image, (x, y), 2, color, 1)
        except Exception as e:
            print(e)


def plan_steering(classified, image):
    height = image.shape[0]
    width = image.shape[1]

    imagified = np.reshape(classified, (height, width))
    c_array = imagified / 5
    cFrame = PyFrame(c_array)

    cFrame.getTapePoints()

    pointList = cFrame.getMidPoints()
    plot_pointlist(image, pointList, (0,100,0))
    midAngle, midOffset = analyseLineScatter(image, pointList, height, width)

    pointList = cFrame.getDarkPoints()
    plot_pointlist(image, pointList, (100, 0, 0))
    blueAngle, blueOffset = analyseLineScatter(image, pointList, height, width)

    pointList = cFrame.getLightPoints()
    plot_pointlist(image, pointList, (0, 0, 100))
    yellowAngle, yellowOffset = analyseLineScatter(image, pointList, height, width)

    angle = 0
    offset = 0
    steering_angle = 0

    # draw the angle
    midx = int(width/2)
    midy = int(height/2)

    if midAngle:
        angle = int(midAngle)
        offset = midOffset
        offset_angle = int(math.degrees(math.atan2(offset, midy)))
        steering_angle = int(int((offset_angle * 2.5 + angle * 7.5) / 10)/2)
    elif blueAngle and yellowAngle:
        angle = int((blueAngle + yellowAngle)/2)
        offset = int((blueOffset + yellowOffset)/2)
        steering_angle = angle
    elif blueAngle:
        angle = int(blueAngle)
        offset = blueOffset
        steering_angle = angle + 8
    elif yellowAngle:
        angle = int(yellowAngle)
        offset = yellowOffset
        steering_angle = angle - 8


    xdiff = int(math.tan(math.radians(angle)) * midy)
    bottomPoint = (midx, height)
    navPoint = (midx + xdiff, midy)
    cv2.line(image, bottomPoint, navPoint, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.line(image, (midx, midy), (midx + offset, midy), (100, 100, 100), 1, cv2.LINE_AA)

    xdiff = int(math.tan(math.radians(steering_angle)) * midy)
    bottomPoint = (midx, height)
    navPoint = (midx + xdiff, midy)
    cv2.line(image, bottomPoint, navPoint, (0, 0, 0), 3, cv2.LINE_AA)

    if SHOW_CAMERA:
        cv2.imshow("res", cv2.resize(image, (1280, 720)))
        if CAMERA:
            cv2.waitKey(1)
        else:
            if cv2.waitKey(0) & 0xFF == ord("q"):
                exit()
    return steering_angle
