import os
import pickle

import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

from utility import choose_file, basic_video_metrics

data_folder = choose_file("training_data")
blue_raw = os.path.join("training_data", data_folder, "blue.csv")
Blue = pd.read_csv(blue_raw)
red_raw = os.path.join("training_data", data_folder, "red.csv")
Red = pd.read_csv(red_raw)
yellow_raw = os.path.join("training_data", data_folder, "yellow.csv")
Yellow = pd.read_csv(yellow_raw)
other_raw = os.path.join("training_data", data_folder, "other.csv")
Other = pd.read_csv(other_raw)

colors = (0,0,0)
area = np.pi*3

X = [255]
Y = [255]
colors = [(0,0,0)]

for i, x in Blue.iterrows():
    X.append(x.H)
    Y.append(x.S)
    colors.append("blue")

for i, x in Yellow.iterrows():
    X.append(x.H)
    Y.append(x.S)
    colors.append("yellow")

for i, x in Red.iterrows():
    X.append(x.H)
    Y.append(x.S)
    colors.append("red")

for i, x in Other.iterrows():
    X.append(x.H)
    Y.append(x.S)
    colors.append("black")


f = plt.figure(1)
plt.scatter(X, Y, c=colors)
plt.xlabel("Hue")
plt.ylabel("Sat")
f.show()

lookupX = []
lookupY = []
lookupColors = []

fp = open("LOOKUP.pkl", "rb")
lookupTable = pickle.load(fp)
for sat, row in enumerate(lookupTable):
    for hue, col in enumerate(row):
        lookupX.append(hue)
        lookupY.append(sat)
        if col == 1:
            lookupColors.append("blue")
        elif col == 2:
            lookupColors.append("red")
        elif col == 3:
            lookupColors.append("yellow")
        else:
            lookupColors.append("black")


g = plt.figure(2)
plt.scatter(lookupX, lookupY, c=lookupColors)
plt.xlabel("Hue")
plt.ylabel("Sat")
g.show()


modify_lookup = input("modify lookup? y or n")
if modify_lookup == 'y':
    cutoff = int(input("sat_cutoff: "))
    yellow_lower = int(input("yellow_lower_cutoff: "))
    yellow_higher = int(input("yellow_higher_cutoff: "))
    blue_lower = int(input("blue_lower_cutoff: "))
    blue_higher = int(input("blue_higher_cutoff: "))
    red_lower = int(input("red_lower_cutoff: "))
    red_higher = int(input("red_higher_cutoff: "))

    lookupTable[:,:] = 4
    lookupTable[cutoff:,blue_lower:blue_higher] = 1
    lookupTable[cutoff:,red_lower:red_higher] = 2
    lookupTable[cutoff:,yellow_lower:yellow_higher] = 3

    lookupX = []
    lookupY = []
    lookupColors = []


    for sat, row in enumerate(lookupTable):
        for hue, col in enumerate(row):
            lookupX.append(hue)
            lookupY.append(sat)
            if col == 1:
                lookupColors.append("blue")
            elif col == 2:
                lookupColors.append("red")
            elif col == 3:
                lookupColors.append("yellow")
            else:
                lookupColors.append("black")

    h = plt.figure(3)
    plt.scatter(lookupX, lookupY, c=lookupColors)
    plt.xlabel("Hue")
    plt.ylabel("Sat")
    h.show()

    fout = open("LOOKUP.pkl", "wb")
    pickle.dump(lookupTable, fout)


    input()

else:
    exit()
