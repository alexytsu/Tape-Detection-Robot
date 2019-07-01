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


try:
    green_raw = os.path.join("training_data", data_folder, "green.csv")
    Green = pd.read_csv(green_raw)
    for i, x in Green.iterrows():
        X.append(x.H)
        Y.append(x.S)
        colors.append("green")
except:
    pass


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


while True:
    modify_lookup = input("modify lookup? y or n")
    if modify_lookup == 'y':
        sat_lower = int(input("sat_lower_cutoff: "))
        sat_higher = int(input("sat_higher_cutoff: "))
        hue_lower = int(input("hue_lower: "))
        hue_higher = int(input("hue_higher: "))
        color = int(input("color: "))

        lookupTable[sat_lower:sat_higher,hue_lower:hue_higher] = color

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
                elif col == 4:
                    lookupColors.append("black")
                elif col == 5:
                    lookupColors.append("green")

        h = plt.figure(3)
        plt.scatter(lookupX, lookupY, c=lookupColors)
        plt.xlabel("Hue")
        plt.ylabel("Sat")
        h.show()

        fout = open("LOOKUP.pkl", "wb")
        pickle.dump(lookupTable, fout)
    else:
        exit()
