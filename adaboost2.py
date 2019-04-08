from sklearn.ensemble import AdaBoostClassifier
from sklearn import datasets
from sklearn import metrics # Metrics module for accuracy calc
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import numpy as np
import argparse
import cv2
import pickle


loaded = None
filename = 'trained.sav'
data = [[24, 178], [23, 219], [23, 212], [22, 221], [23, 177], [24, 221], [24, 63], [24, 204], [23, 137],
[111, 207], [110, 255], [111, 183], [113, 175], [110, 213], [110, 202], [114, 99], [111, 140], [114, 44], 
[140, 5], [120, 4], [126, 11], [8, 11], [132, 13], [140, 6],
[177, 199], [176, 223], [170, 170], [179, 185], [179, 189], [176, 210]]
target = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4]

def train_classifier():
    # 9 Yellows, 9 blues, 6 grounds, 6 reds:

    X = data
    y = target
    groups = ['yellow', 'blue', 'floor', 'red']

    # Split data into 70% training and 30% test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1, random_state = 0) 

    model = GaussianNB()

    # ADABOOST MODEL - uses decision tree as default:

    # Create adaboost classifer object
    abc = AdaBoostClassifier(n_estimators=3, learning_rate=1)

    # Train Adaboost Classifer
    model = abc.fit(X_train, y_train)

    # Predict the response for test dataset
    #y_pred = model.predict(X_test)

    # Model Accuracy, how often is the classifier correct?
    #print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

    pickle.dump(model, open(filename, 'wb'))

# Load the image

def mask_image(image):

    # Convert BGR to HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    H = hsvImage[:,:,0]
    S = hsvImage[:,:,1]

    # find how long the one dimensional form needs to be
    one_dim_length = hsvImage.shape[0] * hsvImage.shape[1]
    # now spread out the image [HSV]
    Xnew = np.reshape(hsvImage, (one_dim_length, 3))
    # only take H and S
    Xnew = Xnew[:,0:2]

    ynew = loaded.predict(Xnew)


    tape = np.where(ynew == 1)
    for i in tape:
            row = int(i / hsvImage.shape[1])
            col = i % hsvImage.shape[1]
            image[row][col] = (ynew[i]*100,200,100)

    image = cv2.resize(image, (100, 100))
    cv2.imshow('res', image)

if __name__ == "__main__":
    train_classifier()
    loaded = pickle.load(open(filename, 'rb'))
    cap = cv2.VideoCapture('footage/test.mp4')

    while(cap.isOpened()):
        ret, frame = cap.read()
        small = cv2.resize(frame, (64, 32))
        mask_image(small)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break