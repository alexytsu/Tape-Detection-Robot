import cv2
import numpy as np

def show_masks(ynew, image, name):
    roi = np.where(ynew == 1)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (0, 200, 100)

    roi = np.where(ynew == 3)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (200, 200, 100)

    roi = np.where(ynew == 4)[0]
    for loc in roi:
        row = int(loc / image.shape[1])
        col = loc % image.shape[1]
        image[row][col] = (0, 0, 0)

    image = cv2.resize(image, (1280, 720))
    cv2.imshow(name, image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        exit()

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
