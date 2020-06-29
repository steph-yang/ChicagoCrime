import pandas as pd
from sodapy import Socrata
import censusdata
import geopandas as gpd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression

import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

import warnings
warnings.filterwarnings('ignore')

import read_facility_data


def normalize(df, df_train, colnames):
    '''
    Normalize dataset on mean and std of training set
    '''
    for column in colnames:
        mean = df_train[column].mean()
        std = df_train[column].std()
        new_col = column+"_norm"
        df[new_col] = df[column].apply(lambda x: (x-mean)/std)
    return df

def loop_linear_reg(times = 20, print_result = False):
    '''
    Compute mean mse and mean r2 in loop
    '''
    mse = []
    r2 = []
    r2_train = []
    mae = []
    var = []
    for t in range(times):
        col = arrest.columns[2:10]
#         col = list(col[:2])+list(col[4:])
        X_train, X_test, y_train, y_test = train_test_split(arrest[col], \
                                                        arrest[arrest.columns[-1:]] , 
                                                        test_size=0.2)
        X_test = normalize(X_test, X_train, X_train.columns)
        X_train = normalize(X_train, X_train, X_train.columns)
        X_train_norm = X_train[[i for i in X_train.columns if i.endswith("_norm")]]
        X_test_norm = X_test[[i for i in X_test.columns if i.endswith("_norm")]]
        
        reg = LinearRegression().fit(X_train_norm, y_train)
        y_train_pred = reg.predict(X_train_norm)
        y_pred = reg.predict(X_test_norm)
        
        mse.append(mean_squared_error(y_test, y_pred))
        r2_train.append(r2_score(y_train, y_train_pred))
        r2.append(r2_score(y_test, y_pred))
        mae.append(mean_absolute_error(y_test, y_pred))
        var.append(reg.score(X_train_norm, y_train))
    
    if print_result:
        print("With {} trials:".format(times))
        print(" Training Data Stat: ")
        print("    Mean R2 = {:.4f}".format(np.mean(r2_train)))
        print("    Mean Variance Score = {:.4f}".format(np.mean(var)))
        print("  Testing Data Stat: ")
        print("    Mean MSE = {:.4f}".format(np.mean(mse)))
        print("    Mean MAE = {:.4f}".format(np.mean(mae)))
        print("    Mean R2 = {:.4f}".format(np.mean(r2)))
        print(" ")

    return (np.mean(r2_train), np.mean(r2))

def bootstrapping(trial, print_result=False):
    r2_train = []
    r2 = []
    for t in trial:
        a, b = loop_linear_reg(t, print_result)
        r2_train.append(a)
        r2.append(b)
    return (r2_train, r2)