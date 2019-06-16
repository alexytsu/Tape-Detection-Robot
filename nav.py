import math
import pdb

import cv2
import numpy as np

from fr import PyFrame
from helper import writeLineAttributes

def plan_steering(classified, image, show_camera):
    """ Decides what angle and speed for the robot to move """

    # get the dimensions of the image and reshape the colour mask
    height = image.shape[0]
    width = image.shape[1]

    # calculate trig values
    midx = int(width/2)
    midy = int(height/2)

    imagified = np.reshape(classified, (height, width))
    image_canonical = np.copy(imagified)

    top_half = imagified[0:midy, : ]
    bottom_half = imagified[midy:height, : ]

    top_angle, top_speed = analyseSegment(top_half, "top", show_camera)
    bottom_angle, bottom_speed = analyseSegment(bottom_half, "bottom_half", show_camera)

    return bottom_angle, bottom_speed


def analyseSegment(image, footage_name, show_camera):
    # get the dimensions of the image and reshape the colour mask
    height = image.shape[0]
    width = image.shape[1]

    # calculate trig values
    midx = int(width/2)
    midy = int(height/2)

    # give the colored frame to Cython to extract lines
    cFrame = PyFrame(image)

    # classify all the necessary points
    cFrame.getTapePoints()

    pointList = cFrame.getMidPoints()
    if show_camera:
        plot_pointlist(image, pointList, (50,255,50))
    midAngle, midOffset = analyseLineScatter(image, pointList, height, width)

    pointList = cFrame.getDarkPoints()
    if show_camera:
        plot_pointlist(image, pointList, (255,50,50))
    blueAngle, blueOffset = analyseLineScatter(image, pointList, height, width)

    pointList = cFrame.getLightPoints()
    if show_camera:
        plot_pointlist(image, pointList, (0, 100, 100))
    yellowAngle, yellowOffset = analyseLineScatter(image, pointList, height, width)

    angle = 0
    offset = 0
    steering_angle = 0

    speed = 95 # default speed
    errorBias = 10

    if midAngle:
        # follow the middle of the lane
        angle = int(midAngle)
        offset = midOffset
        offset_angle = int(math.degrees(math.atan2(offset, midy)))
        steering_angle = int((offset_angle * 9 + angle * 1) / 10)
    elif blueAngle and yellowAngle:
        # rotate and find a better midline
        angle = int((blueAngle + yellowAngle)/2)
        offset = int((blueOffset + yellowOffset)/2)
        steering_angle = angle
    elif blueAngle:
        # only see blue tape
        angle = int(blueAngle)
        offset = blueOffset
        steering_angle = angle * 1.5 + errorBias # shift away from the blue tape
    elif yellowAngle:
        # only see yellow tape
        angle = int(yellowAngle)
        offset = yellowOffset
        steering_angle = angle * 1.5 - errorBias # shift away from yellow tape
    else:
        steering_angle = 0 # hold the line

    # plot all the spaghetti for debugging
    if show_camera:
        try:
            xdiff = int(math.tan(math.radians(angle)) * midy)
            bottomPoint = (midx, height)
            navPoint = (midx + xdiff, midy)
            cv2.line(image, bottomPoint, navPoint, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.line(image, (midx, midy), (midx + offset, midy), (100, 100, 100), 1, cv2.LINE_AA)

            xdiff = int(math.tan(math.radians(steering_angle)) * midy)
            bottomPoint = (midx, height)
            navPoint = (midx + xdiff, midy)
            cv2.line(image, bottomPoint, navPoint, (255, 255, 255), 3, cv2.LINE_AA)
        except:
            print("failed to draw some lines")
            pass

        cv2.imshow(footage_name, cv2.resize(image, (1280, 720)))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit()

    return steering_angle, speed


class AngleBuffer():
    def __init__(self, length):
        self.length = length
        self.current = 0
        self.buffer = [0] * length
    
    def add_new(self, angle):
        self.buffer[self.current % self.length] = angle
        self.current += 1

    def get_angle(self):
        return int(sum(self.buffer) / self.length)

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
    """ Fit lines to a scatter and find attributes """
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

    # LOWER NUMBER === MOREEE SPAGHETTIIII
    SPAGHETTI = 15

    lines = cv2.HoughLines(blank_image, 4, np.pi / 50, SPAGHETTI, None, 0, 0)
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
            cv2.circle(image, (x, y), 2, color, 2)
        except Exception as e:
            print(e)


