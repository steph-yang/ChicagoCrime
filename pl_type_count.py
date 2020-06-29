import pandas as pd
import geopandas as gpd

import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

import warnings
warnings.filterwarnings('ignore')

################ Set Variable ######################


df = "ChicagoCrimeCases2019.csv"


################ Read Csv File ######################

def read_crime_all(df):
    '''
    Read in all crime cases data in Chicago
    '''
    crime = pd.read_csv(df)
    crime = crime.dropna()
    crs = {"init":"epsg:4326"}
    crime = gpd.GeoDataFrame(crime, crs = crs, geometry=gpd.points_from_xy(crime.Longitude, crime.Latitude))
    crime = gpd.sjoin(crime, neighborhood, how="inner", op='intersects')
    return crime


################ Create Histogram ######################

def histogram(crime):
    plt.figure(figsize=(10, 20))
    plot = sns.countplot(y="Primary Type", data=crime,\
	                 order = crime['Primary Type'].value_counts(ascending=True).iloc[8:].index)
    plot.set_xticklabels(plot.get_xticklabels(), rotation=90,
	                     fontsize=8.5)
    for p in plot.patches:
        width = p.get_width()
	plot.text(width + 100,
	          p.get_y()+p.get_height()/2.,
	          '{}'.format(width),
	           ha="center") 
    plot.axes.set_title("Count of Different Type of Crimes",fontsize=20)
    # plot.set_xlabel("Crime Type",fontsize=20)
    # plot.set_ylabel("Count",fontsize=15)
    plot


################ Pull Together ######################

def go(df):
    crime = read_crime_all(df)
    histogram(crime)
