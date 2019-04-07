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
import time
 
import pdb

def shit_the_bed():
    print("UWUUUUU FUCKY WUCKY")
    pdb.set_trace()


# 9 Yellows, 9 blues:
data = [[24, 178], [23, 219], [23, 212], [22, 221], [23, 177], [24, 221], [24, 63], [24, 204], [23, 137],
[111, 207], [110, 255], [111, 183], [113, 175], [110, 213], [110, 202], [114, 99], [111, 140], [114, 44]]

target = [2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1]

X = data
y = target
groups = ['yellow', 'blue']

# Split data into 70% training and 30% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0) 

model = GaussianNB()
#mnb = MultinomialNB()

#y_pred_gnb = gnb.fit(X_train, y_train).predict(X_test)
#cnf_matrix_gnb = confusion_matrix(y_test, y_pred_gnb)

#print the confusion matrix print(cnf_matrix_gnb)

"""y_pred_mnb = mnb.fit(X_train, y_train).predict(X_test)
cnf_matrix_mnb = confusion_matrix(y_test, y_pred_mnb)
 
print(cnf_matrix_mnb)"""

# ADABOOST MODEL - uses decision tree as default:

# Create adaboost classifer object
abc = AdaBoostClassifier(n_estimators=7, learning_rate=1)

# Train Adaboost Classifer
model = abc.fit(X_train, y_train)

# Predict the response for test dataset
#y_pred = model.predict(X_test)

# Model Accuracy, how often is the classifier correct?
#print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

filename = 'trained.sav'
pickle.dump(model, open(filename, 'wb'))

# Load the image
for i in range(1,45):
    image = cv2.imread(f"images/my_photo-{i}.jpg")

    # Convert BGR to HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # find how long the one dimensional form needs to be
    one_dim_length = hsvImage.shape[0] * hsvImage.shape[1]
    # now spread out the image [HSV]
    Xnew = np.reshape(hsvImage, (one_dim_length, 3))
    # only take H and S
    Xnew = Xnew[:,0:2]

    """
    H = hsvImage[:,:,0]
    S = hsvImage[:,:,1]
    Xnew = list()


    range1 = H.shape[0]
    range2 = H.shape[1]
    for value in range(range1): #[0,1...719]
        for value2 in range(range2):
            Xnew.append([H[value][value2], S[value][value2]])

    """


    loaded = pickle.load(open(filename, 'rb'))
    result = loaded.score(X_test, y_test)

    ynew = model.predict_proba(Xnew)
    print(ynew)


    for i in range(len(Xnew)):
        if ynew[i][1] > 0.99:
            row = int(i / 1280)
            col = i % 1280
            hsvImage[row][col] = (0,0,0)

    cv2.imshow('res',hsvImage)
cv2.waitKey(0)
cv2.destroyAllWindows()

