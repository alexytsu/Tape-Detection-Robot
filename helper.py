import cv2
import numpy as np

def show_masks(ynew, image, name, w, h):
    roi = np.where(ynew == 1)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (200, 50, 50)

    roi = np.where(ynew == 3)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (0, 200, 250)

    roi = np.where(ynew == 2)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (50, 50, 200)

    roi = np.where(ynew == 4)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (0, 0, 0)

    roi = np.where(ynew == 5)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (50, 255, 20)

    roi = np.where(ynew == 6)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (255, 50, 200)

    image = cv2.resize(image, (w, h))
    return image

def writeLineAttributes(lat, angle, steer, image):
    cv2.putText(
        image,
        f"Lateral Error: {lat:.2f}",
        (10, 15),
        cv2.FONT_HERSHEY_PLAIN,
        1,
        (255, 255, 0),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        f"Angular Error: {angle:.2f}",
        (10, 30),
        cv2.FONT_HERSHEY_PLAIN,
        1,
        (255, 255, 0),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        f"Steering Angle: {steer:.2f}",
        (10, 45),
        cv2.FONT_HERSHEY_PLAIN,
        1,
        (255, 255, 0),
        1,
        cv2.LINE_AA,
    )
