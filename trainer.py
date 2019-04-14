import os
import pdb
import pickle

import _tkinter
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.ensemble import AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

def train_classifier(data_folder):

    blue_raw = os.path.join("training_data", data_folder, "blue.csv")
    Blue = pd.read_csv(blue_raw)
    red_raw = os.path.join("training_data", data_folder, "red.csv")
    Red = pd.read_csv(red_raw)
    yellow_raw = os.path.join("training_data", data_folder, "yellow.csv")
    Yellow = pd.read_csv(yellow_raw)
    other_raw = os.path.join("training_data", data_folder, "other.csv")
    Other = pd.read_csv(other_raw)

    X = []
    Hues = []
    Sats = []
    y = []

    for i, x in Blue.iterrows():
        X.append([x.H, x.S])
        y.append(1)

    for i, x in Red.iterrows():
        X.append([x.H, x.S])
        y.append(2)

    for i, x in Yellow.iterrows():
        X.append([x.H, x.S])
        y.append(3)

    for i, x in Other.iterrows():
        X.append([x.H, x.S])
        y.append(4)

    # plt.scatter()
    # classifier = AdaBoostClassifier(n_estimators=3, learning_rate=1) 
    classifier = GaussianNB()
    #classifier = GaussianProcessClassifier(1.0 * RBF(1.0))
    model = classifier.fit(X,y)



    filepath = os.path.join("trained_models", "Adaboost", "model.sav")
    pickle.dump(model, open(filepath,'wb'))

if __name__ == "__main__":
    data = input("Foldername: ")
    train_classifier(data)
