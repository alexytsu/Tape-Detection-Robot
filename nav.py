import math
import pdb

import cv2
import numpy as np

from fr import PyFrame
from helper import writeLineAttributes

def get_box_ratio(box):
    a, b, c, d = box
    a1, a2 = a
    b1, b2 = b
    c1, c2 = c
    dist_1 = math.sqrt((a1 - b1) ** 2 + (a2 - b2) ** 2 )
    dist_2 = math.sqrt((c1 - b1) ** 2 + (c2 - b2) ** 2 )
    return max(dist_1/dist_2, dist_2/dist_1)

def get_endpoints_of_longest_edge(box):
    a, b, c, d = box
    a1, a2 = a
    b1, b2 = b
    c1, c2 = c
    dist_1 = math.sqrt((a1 - b1) ** 2 + (a2 - b2) ** 2 )
    dist_2 = math.sqrt((c1 - b1) ** 2 + (c2 - b2) ** 2 )
    x1, x2, y1, y2 = None

    if(dist_1 < dist2):
        return (b, c)
    else:
        return (a, b)


def plan_steering(classified, image, further_classified, further_image, show_camera):

    # get dimensions of the frame
    height = image.shape[0]
    width = image.shape[1]
    midx = int(width/2)
    midy = int(height/2)

    # turn the colour mask into an "image"
    imagified = np.reshape(classified, (height, width))

    angle = 0
    offset = 0
    steering_angle = 0
    speed = 95

    blue_info = None
    yellow_info = None

    # get blue tape
    blue_contours, blue_lines = extract_tape(1, imagified, height, width, image)
    rectangles = list(map(cv2.minAreaRect, blue_contours))
    boxes = list(map(cv2.boxPoints, rectangles))
    boxes = list(map(np.int0, boxes))
    boxes = sorted(boxes, key=get_box_ratio, reverse=True)
    try:
        box = boxes[0]
        cv2.drawContours(image, [box], 0, (0, 0, 200), 2)
        pointa, pointb = get_endpoints_of_longest_edge(box)
        
    except:
        pass

    # yellow tape
    yellow_contours, yellow_lines = extract_tape(3, imagified, height, width, image)
    rectangles = list(map(cv2.minAreaRect, yellow_contours))
    boxes = list(map(cv2.boxPoints, rectangles))
    boxes = list(map(np.int0, boxes))
    boxes = sorted(boxes, key=get_box_ratio, reverse=True)
    try:
        box = boxes[0]
        cv2.drawContours(image, [box], 0, (0, 0, 200), 2)
    except:
        pass

    # obstacle avoidance
    red_loc = (imagified ==2).astype(int)
    contours, _ = cv2.findContours(red_loc, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = list(map(cv2.contourArea, contours))
    blueOffset = midx
    yellowOffset = midx

    contours = list(filter(lambda x: cv2.contourArea(x) > 1000 and cv2.contourArea(x) < 4000, contours))
    contours = sorted(contours, key= lambda x: cv2.contourArea(x), reverse=False)
    if len(contours) > 0:
        x, y, w, h = cv2.boundingRect(contours[0])
        cv2.rectangle(image, (x, y), (x+w,y+h), (255, 255, 0))
        cv2.drawContours(image, contours, 0, (255, 0, 255), 0)

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


    cv2.imshow("res", cv2.resize(image, (500, 720)))
    if cv2.waitKey(1) & 0xFF == ord("q"):
        exit()

    return steering_angle, speed


def extract_tape(colour, imagified, height, width, image):
    # get blue tape
    tape_loc = (imagified == colour).astype(int)

    # exclude certain areas
    if colour == 1:
        tape_loc[0:int(3*height/4),:] = 0 
        tape_loc[:, int(3*width/4):width] = 0 
    elif colour == 3:
        tape_loc[0:int(3*height/4),:] = 0 
        tape_loc[:, 0:int(width/4)] = 0 

    # find the blue tape contours
    contours, _ = cv2.findContours(tape_loc, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # get rid of the teeny tiny ones
    contours = list(filter(lambda x: cv2.contourArea(x) > 20, contours))

    # filter on the snakiness
    contour_snake = list(map(lambda cnt: cv2.arcLength(cnt, True)/cv2.contourArea(cnt), contours))
    contour_snake = sorted(contour_snake, reverse=True)
    print("Snakiness", contour_snake)
    contours = list(filter(lambda x: cv2.arcLength(x, True)/cv2.contourArea(x) > 0.4, contours))

    # draw all the contours
    cv2.drawContours(image, contours, -1, (255, 100, 255), 0)

    # fit lines to the contours
    contour_lines = list(map(lambda contours: cv2.fitLine(contours, cv2.DIST_L2, 0,0,0.01,0.01), contours))
    return contours, contour_lines


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


