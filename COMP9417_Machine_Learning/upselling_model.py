# Python version 3.6.0
# Pandas version 0.20.1
#
# Written by Juliana Zhu for 
# COMP9417 Machine Learning & Data Mining 17s1
# Assignment 2 - Machine Learning Project
# Topic 8: Work on a past KDD Cup competition task
# KDD Cup 2009: Customer Relationship Prediction

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler, Imputer, MinMaxScaler, scale
from sklearn.model_selection import KFold
from sklearn.metrics import roc_curve, auc

from sklearn.linear_model import Lasso


KFOLDS = 10


# Returns preprocessed features as a Numpy matrix
def preprocess_data(dataset):
    output_dataset = (len(dataset), len(dataset.index))

    binary_encode = []
    one_hot_encode = []
    scaling = []

    # Drop NULL columns
    # Can set 'Thresh' later to require that many non-NA values before dropping
    dataset.dropna(inplace=True, axis=1, how='all', thresh=None)

    for c in dataset.columns:
        # Binary feature columns
        if len(dataset[c].unique()) <= 2 and dataset[c].isnull().values.any():
            binary_encode.append(c)
        # String data type columns (Non-binary)
        elif dataset[c].dtype == object:
            most_freq_val_count = dataset[c].value_counts().max()
            # If one value dominates the feature, turn it into a binary feature
            if most_freq_val_count / len(dataset.index) > 0.80:
                value_counts = dataset[c].value_counts()
                to_remove = value_counts[value_counts < most_freq_val_count].index
                dataset[c].replace(to_remove, np.nan, inplace=True)
                binary_encode.append(c)
            # One-hot encode features with up to 3 unique values
            elif len(dataset[c].unique()) <= 3:
                one_hot_encode.append(c)
            # Replace values with their counts and then put them in 3 bins
            else:
                dataset[c].fillna('None', inplace=True)
                df = dataset[c].to_frame()
                index = c +'freq'
                df[index] = df.groupby(c)[c].transform('count')
                del df[c]
                dataset[c] = pd.qcut(df[index], 3, duplicates='drop')
                one_hot_encode.append(c)

        # Numerical columns (Non-binary)
        else:
            # Impute missing values using the mean
            imputer = Imputer()
            dataset[c] = imputer.fit_transform(dataset[c].as_matrix().reshape(-1, 1))
            # Assume that a column with more than 1000 unique values
            # Is continuous and bin them
            if len(dataset[c].unique()) > 1000:
                dataset[c] = pd.qcut(dataset[c], 10, duplicates='drop')
            # Scale the resulting value                
            dataset[c] = preprocessing.scale(dataset[c].as_matrix().reshape(-1, 1))
            Use MinMaxScaler for MNBayes
            dataset[c] = MinMaxScaler().fit_transform(dataset[c].as_matrix().reshape(-1, 1))

    # Perform the actual encoding
    dataset = pd.get_dummies(dataset, prefix=one_hot_encode, columns=one_hot_encode)
    dataset = pd.get_dummies(dataset, prefix=binary_encode, columns=binary_encode, drop_first=bool)
    dataset.to_csv("processed_dataset.csv")
    return dataset.as_matrix()


def train_model(x_train, y_train):
    classifier = Lasso()
    model = classifier.fit(x_train, y_train)
    return model


def predict_results(model, x_test, y_test):
    print("True values: ", y_test.as_matrix())
    prediction = model.predict(x_test)
    print("Predicted: ", prediction)
    fpr, tpr, thresholds = roc_curve(y_test, prediction, pos_label=1)
    print("False Positive rate: ", fpr, "\n True positive rate: ", tpr)
    score = auc(fpr, tpr)
    return score


################ Main #################
X_dataset = pd.read_csv('x_train.csv')
Y_dataset = pd.read_csv('Upselling_train.csv')

X_dataset = preprocess_data(X_dataset)
Y_dataset = Y_dataset['Upselling'] 


results = []
kf = KFold(n_splits=KFOLDS)
n = 1
for train_index, test_index in kf.split(X_dataset):
    print("Classifying fold", n, "of 10:")
    print("TRAIN:", train_index, "TEST:", test_index)
    x_train, x_test = X_dataset[train_index], X_dataset[test_index]
    y_train, y_test = Y_dataset[train_index], Y_dataset[test_index]
    model = train_model(x_train, y_train)
    score = predict_results(model, x_test, y_test)
    print("Result = ", score)
    results.append(score)
    print("-----------------------------------------------")
    n += 1

results = np.asarray(results)
print("Results Mean: ", results.mean())
print("Standard Deviation: ", results.std())
