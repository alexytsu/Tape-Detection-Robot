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


# 9 Yellows, 9 blues, 6 grounds, 6 reds:
data = [[24, 178], [23, 219], [23, 212], [22, 221], [23, 177], [24, 221], [24, 63], [24, 204], [23, 137],
[111, 207], [110, 255], [111, 183], [113, 175], [110, 213], [110, 202], [114, 99], [111, 140], [114, 44], 
[140, 5], [120, 4], [126, 11], [8, 11], [132, 13], [140, 6],
[177, 199], [176, 223], [170, 170], [179, 185], [179, 189], [176, 210]]

target = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4]

X = data
y = target
groups = ['yellow', 'blue', 'floor', 'red']

# Split data into 70% training and 30% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1, random_state = 0) 

model = GaussianNB()

# ADABOOST MODEL - uses decision tree as default:

# Create adaboost classifer object
abc = AdaBoostClassifier(n_estimators=20, learning_rate=1)

# Train Adaboost Classifer
model = abc.fit(X_train, y_train)

# Predict the response for test dataset
#y_pred = model.predict(X_test)

# Model Accuracy, how often is the classifier correct?
#print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

filename = 'trained.sav'
pickle.dump(model, open(filename, 'wb'))

# Load the image
for x in range(1,45):
    image = cv2.imread(f"images/my_photo-{x}.jpg")

    # Convert BGR to HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    H = hsvImage[:,:,0]
    S = hsvImage[:,:,1]
    Xnew = list()

    # find how long the one dimensional form needs to be
    one_dim_length = hsvImage.shape[0] * hsvImage.shape[1]
    # now spread out the image [HSV]
    Xnew = np.reshape(hsvImage, (one_dim_length, 3))
    # only take H and S
    Xnew = Xnew[:,0:2]

    loaded = pickle.load(open(filename, 'rb'))
    result = loaded.score(X_test, y_test)

    ynew = model.predict(Xnew)

    for i in range(len(ynew)):
        if ynew[i] == 1 or ynew[i] == 2:
            row = int(i / 1280)
            col = i % 1280
            hsvImage[row][col] = (0,0,0)

    cv2.imshow(f'res{x}',hsvImage)
cv2.waitKey(0)
cv2.destroyAllWindows()