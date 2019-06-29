import math
import pdb

import cv2
import numpy as np

from fr import PyFrame
from helper import writeLineAttributes

def plan_steering(classified, image, further_classified, further_image, show_camera):
    height = image.shape[0]
    width = image.shape[1]

    imagified = np.reshape(classified, (height, width))
    c_array = imagified
    cFrame = PyFrame(c_array)

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

    # draw the angle
    midx = int(width/2)
    midy = int(height/2)

    speed = 95

    # obstacle avoidance
    red_loc = (imagified ==2).astype(int)
    contours, _ = cv2.findContours(red_loc, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    #contour_sizes = list(map(cv2.contourArea, contours))
    #print(contour_sizes)

    if midAngle:
        angle = int(midAngle)
        offset = midOffset
        offset_angle = int(math.degrees(math.atan2(offset, midy)))
        steering_angle = int((offset_angle * 5 + angle * 5) / 10)
    elif blueAngle and yellowAngle:
        angle = int((blueAngle + yellowAngle)/2)
        offset = int((blueOffset + yellowOffset)/2)
        steering_angle = angle * 1.5
    elif blueAngle:
        angle = int(blueAngle)
        offset = blueOffset
        steering_angle = angle * 1.5 + 15
    elif yellowAngle:
        angle = int(yellowAngle)
        offset = yellowOffset
        steering_angle = angle * 1.5 - 15
    else:
        steering_angle = 0

    contours = list(filter(lambda x: cv2.contourArea(x) > 4000 and cv2.contourArea(x) < 10000, contours))
    contours = sorted(contours, key= lambda x: cv2.contourArea(x), reverse=False)
    if len(contours) > 0:
        x, y, w, h = cv2.boundingRect(contours[0])
        cv2.rectangle(image, (x, y), (x+w,y+h), (255, 255, 0))
        cv2.drawContours(image, contours, 0, (255, 0, 255), 0)

        if not blueAngle:
            blueOffset = -int(width)
        if not yellowAngle:
            yellowOffset = int(width)

        left_edge_offset = x - midx
        right_edge_offset = x + h - midx

        left_gap = abs(blueOffset - left_edge_offset)
        right_gap = abs(yellowOffset - right_edge_offset)


        if left_gap > right_gap:
            avoid_offset = blueOffset + (x - midx)
            avoid_offset = avoid_offset/2
            angle_radians = math.atan2(avoid_offset, height - (y+h))
            steering_angle = int(math.degrees(angle_radians))
        else:
            avoid_offset = yellowOffset + (x + h - midx)
            avoid_offset = avoid_offset/2
            angle_radians = math.atan2(avoid_offset, height - (y+h))
            steering_angle = int(math.degrees(angle_radians))



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
            cv2.line(image, bottomPoint, navPoint, (255, 50, 150), 3, cv2.LINE_AA)
        except:
            print("failed to draw some lines")
            pass


        cv2.imshow("res", cv2.resize(image, (600, 600)))
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
    # gradientIntercept(line, height)
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

    # LOWER NUMBER === MOREEE SPAGHETTIIII
    SPAGHETTI = 17

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


