import math
import pdb

import cv2
import numpy as np

from fr import PyFrame
from helper import writeLineAttributes

def plan_steering(classified, image, show_camera):

    height = image.shape[0]
    width = image.shape[1]
    midx = int(width/2)
    midy = int(height/2)

    imagified = np.reshape(classified, (height, width))

    # split image in two
    divider = int(3*height/6)
    imagifiedTop = imagified[:divider, :]
    imagifiedBottom = imagified[divider:, :]
    imageTop = image[:divider, :]
    imageBottom = image[divider:, :]

    # split analysis on top and bottom half
    bottom_angle, bottomAux = analyse_half(
        "bottom", imagifiedBottom, imageBottom, show_camera)
    top_angle, topAux = analyse_half(
        "top", imagifiedTop, imageTop, show_camera)

    steering_angle, speed = decideBehaviour(bottom_angle, top_angle)

    """
    OBSTACLE AVOIDANCE OVERRIDE
    """
    red_loc = (imagified ==2).astype(int)
    contours, _ = cv2.findContours(red_loc, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    #contour_sizes = list(map(cv2.contourArea, contours))
    #print(contour_sizes)

    contours = list(filter(lambda x: cv2.contourArea(x) > 1500 and cv2.contourArea(x) < 10000, contours))
    contours = sorted(contours, key= lambda x: cv2.contourArea(x), reverse=False)
    if len(contours) > 0:
        steering_angle = avoidObstacles(contours, image, bottomAux, width, midx, height, steering_angle)
        speed = 0

    """
    DEBUGGING STUFF
    """

    """
    STOPPING STUFF
    """
    saw_tape = False
    stop_loc = (imagified == 5).astype(int)
    contours, _ = cv2.findContours(stop_loc, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key= lambda x: cv2.contourArea(x), reverse=False)
    contour_sizes = list(map(cv2.contourArea, contours))
    print(contour_sizes)
    contours = list(filter(lambda x: cv2.contourArea(x) > 500 and cv2.contourArea(x) < 2000, contours))
    cv2.drawContours(image, contours, -1, (200, 30, 30), 0)
    if len(contours) > 0:
        saw_tape = True



    angle = 0
    offset = 0

    if show_camera:
        try:
            xdiff = int(math.tan(math.radians(steering_angle)) * midy)
            bottomPoint = (midx, height)
            navPoint = (midx + xdiff, midy)
            cv2.line(image, bottomPoint, navPoint,
                     (255, 50, 150), 3, cv2.LINE_AA)
        except Exception as e:
            print("failed to draw main navigation line: ", e)
            pass

        speedMessages = ["OBSTACLE", "TURN", "NORMAL", "TURBO"]
        cv2.putText(image, speedMessages[speed], (10, 30),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA,)
        cv2.imshow("res", cv2.resize(image, (600, 600)))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit()

    return steering_angle, speed, saw_tape

def analyse_half(half, classified_image, image, show_camera):
    cFrame = PyFrame(classified_image)
    height = image.shape[0]
    width = image.shape[1]

    midx = int(width/2)
    midy = int(height/2)
    
    cFrame.getTapePoints(half == "top")
    pointList = cFrame.getMidPoints()
    if show_camera:
        plot_pointlist(image, pointList, (50, 255, 50))
    midAngle, midOffset = analyseLineScatter(image, pointList, height, width)
    pointList = cFrame.getDarkPoints()
    if show_camera:
        plot_pointlist(image, pointList, (255, 50, 50))
    blueAngle, blueOffset = analyseLineScatter(image, pointList, height, width)
    pointList = cFrame.getLightPoints()
    if show_camera:
        plot_pointlist(image, pointList, (0, 100, 100))
    yellowAngle, yellowOffset = analyseLineScatter(
        image, pointList, height, width)

    if show_camera:
        print(f"Debugging info for the {half} half")
        print(f"mid {(midAngle, midOffset)}")
        print(f"blue {(blueAngle, blueOffset)}")
        print(f"yellow {(yellowAngle, yellowOffset)}")

    auxInfo = {
        "mid": (midAngle, midOffset),
        "blue": (blueAngle, blueOffset),
        "yellow": (yellowAngle, yellowOffset)
    }

    """
    navigation stuff
    """
    angle = 0
    offset = 0
    steering_angle = 0
    speed = 0

    # stuff to tune
    angleMultiplier = 2
    correctionOffset = 30

    if midAngle:
        angle = int(midAngle)
        offset = midOffset
        offset_angle = int(math.degrees(math.atan2(offset, midy)))
        steering_angle = int(
            (offset_angle * 7 + angle * 3) / 10) * angleMultiplier
    elif blueAngle and yellowAngle:
        angle = int((blueAngle + yellowAngle)/2)
        offset = int((blueOffset + yellowOffset)/2)
        steering_angle = angle * angleMultiplier
    elif blueAngle:
        angle = int(blueAngle)
        offset = blueOffset
        steering_angle = min(angle * angleMultiplier + correctionOffset, 60)
        if offset > 0:
            steering_angle = 60
    elif yellowAngle:
        angle = int(yellowAngle)
        offset = yellowOffset
        steering_angle = max(angle * angleMultiplier - correctionOffset, -60)
        if offset < 0:
            steering_angle = -70
    else:
        steering_angle = None

    if show_camera:
        try:
            xdiff = int(math.tan(math.radians(angle)) * midy)
            bottomPoint = (midx, height)
            navPoint = (midx + xdiff, midy)
            cv2.line(image, bottomPoint, navPoint, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.line(image, (midx, midy), (midx + offset, midy),
                     (100, 100, 100), 1, cv2.LINE_AA)
            xdiff = int(math.tan(math.radians(steering_angle)) * midy)
            bottomPoint = (midx, height)
            navPoint = (midx + xdiff, midy)
            cv2.line(image, bottomPoint, navPoint,
                     (255, 100, 200), 1, cv2.LINE_AA)
        except:
            print("failed to draw some lines")
            pass

        cv2.imshow(half, cv2.resize(image, (600, 600)))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit()

    return steering_angle, auxInfo



def avoidObstacles(contours, image, bottomAux, width, midx, height, steering_angle):
    x, y, w, h = cv2.boundingRect(contours[0])
    cv2.rectangle(image, (x, y), (x+w,y+h), (255, 255, 0))
    cv2.drawContours(image, contours, 0, (255, 0, 255), 0)

    blueAngle, blueOffset = bottomAux["blue"]
    yellowAngle, yellowOffset = bottomAux["yellow"]

    if not blueAngle:
        blueOffset = -int(width)
    if not yellowAngle:
        yellowOffset = int(width)

    left_edge_offset = x - int(width/2)
    right_edge_offset = x + w - int(width/2)

    left_gap = left_edge_offset - blueOffset
    right_gap = yellowOffset - right_edge_offset

    if left_gap > right_gap:
        avoid_offset = blueOffset + (x - midx)
        avoid_offset = avoid_offset/2
        angle_radians = math.atan2(avoid_offset, height - (y+h))
        steering_angle = -50
        #steering_angle = int(math.degrees(angle_radians)) * 2
    else:
        avoid_offset = yellowOffset + (x + h - midx)
        avoid_offset = avoid_offset/2
        angle_radians = math.atan2(avoid_offset, height - (y+h))
        #steering_angle = int(math.degrees(angle_radians)) * 2
        steering_angle = 50

    return steering_angle

def decideBehaviour(bottom_angle, top_angle):
    steering_angle = 0
    speed = 0

    if bottom_angle is None and top_angle is None:
        # no tape
        steering_angle = 0
        speed = 2
    elif bottom_angle is None:
        # only top tape
        steering_angle = top_angle
        # faster when straighter
        if abs(steering_angle) < 15:
            speed = 2
        else:
            speed = 1
    elif top_angle is None:
        # only bottom tape
        steering_angle = bottom_angle
        # faster when straight
        if abs(steering_angle) < 15:
            speed = 2
        else:
            speed = 1
    else:
        # both tapes    
        # tune
        steering_angle = (2*bottom_angle + top_angle)/3
        swerve = top_angle * bottom_angle < 0
        largeDiff = abs(top_angle - bottom_angle) > 30

        if swerve and largeDiff:
            speed = 1
        elif swerve:
            speed = 2
        elif largeDiff:
            speed = 1
        else:
            speed = 2
            if(abs(steering_angle) < 15):
                speed = 3
    return steering_angle, speed


class AngleBuffer():
    def __init__(self):
        self.previous = 0
        self.current = 0

    def add_new(self, angle):
        self.previous = self.current
        self.current = angle

    def get_angle(self):
        return int((previous + current)/2)


def getLineAttributes(line, width, height):
    lateral_error = 0
    end, start = line
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
    SPAGHETTI = 16

    lines = cv2.HoughLines(blank_image, 2, np.pi / 200, SPAGHETTI, None, 0, 0)
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
