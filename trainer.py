import os
import pdb
import pickle

import _tkinter
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.neighbors import KNeighborsClassifier

from utility import choose_file

def train_classifier(data_folder, classifier_name):

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
    if classifier_name == "adaboost":
        classifier = AdaBoostClassifier(n_estimators=10, learning_rate=1) 
    elif classifier_name == "gaussian":
        classifier = GaussianNB()
    # classifier = GaussianProcessClassifier(1.0 * RBF(1.0))
    elif classifier_name == "kneighbors":
        classifier = KNeighborsClassifier(3)
    # classifier = RandomForestClassifier(max_depth=5, n_estimators=5, max_features=1)
    else:
        print("NO VALID CLASSIFIER SELECTED")
        exit()

    model = classifier.fit(X,y)

    try:
        os.mkdir(os.path.join("trained_models", data_folder))
    except FileExistsError:
        pass

    filepath = os.path.join("trained_models", data_folder, "model.sav")
    pickle.dump(model, open(filepath,'wb'))
    return model


def create_lookup(classifier, data, model, path=None):
    try:
        os.mkdir(os.path.join("trained_models", data))
    except FileExistsError:
        pass
    saved_path = os.path.join("trained_models", data, classifier+"_lookup.sav")
    COLOR_LOOKUP = np.zeros((256,256), dtype= np.uint8)
    for h in range(256):
        for s in range(256):
            answers = ["NONE", "BLUE", "RED", "YELLOW", "OTHER"]
            result =  model.predict([np.array([h,s])])[0]
            if result == 1 or result == 3:
                print(f"Storing H:{h} with S:{s} as {answers[result]} {result}")
            COLOR_LOOKUP[h][h] = int(result)
    
    if not path is None:
        file = open(path, "wb")
        pickle.dump(COLOR_LOOKUP, file)
    
    file = open(saved_path, "wb")
    pickle.dump(COLOR_LOOKUP, file)

if __name__ == "__main__":
    data = choose_file("training_data")
    classifier = input("Classifier: ")
    model = train_classifier(data, classifier)
    create_lookup(classifier, data, model, os.path.join("LOOKUP.pkl"))
