import os

import cv2

def choose_file(folder):
    """
    Let the user choose the file they wish to work on
    """
    
    # List all the video files we have 
    video_files = os.listdir(folder)
    n_files = len(video_files)
    for idx, video in enumerate(video_files):
        print(f"[{idx}]: {video}")

    file_n = input(f"Select the video file (0-{n_files-1}): ")
    try:
        file_n = int(file_n)
        if(file_n >= n_files):
            print("Invalid file index chosen")
            exit()
    except:
        print("Invalid file selection")
        exit()
    
    filename = video_files[file_n]
    return filename
    
def basic_video_metrics(filename):
    """
    Get the height, width, fps and length of the footage
    """
    filepath = os.path.join("footage", filename)
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise Exception("No footage found: ", filepath)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    return width, height, length, fps