import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from folium import plugins
import matplotlib.pyplot as plt
import seaborn as sns
import censusdata
import numpy as np

%matplotlib inline

import warnings
warnings.filterwarnings('ignore')

################ Set Variable ######################


df = "ChicagoCrimeCases2019.csv"


################ Read Csv File ######################

def read_data(df, type_ = "HOMICIDE"):
	'''
	Read in Chicago Crime Case Data
	Input:
		df: name of the csv file
		type_: type of crime cases
	Output:
		df
	'''
	crime = pd.read_csv(df)

	neighborhood = gpd.read_file("Boundaries - Neighborhoods.geojson")
	crime = crime.dropna()
	crs = {"init":"epsg:4326"}
	crime = gpd.GeoDataFrame(crime, crs = crs, geometry=gpd.points_from_xy(crime.Longitude, \
							crime.Latitude))
	crime = gpd.sjoin(crime, neighborhood, how="inner", op='intersects')

	crime_truncated = crime[crime["Primary Type"] == type_]

	return crime_truncated


################# Create Heat Map #####################


def heat_map(crime_truncated):
	'''
	Create Interactive Heat Map on Google Map
	'''
	m = folium.Map([41.8781, -87.6298], zoom_start=11)
	for index, row in crime_truncated.iterrows():
	    folium.CircleMarker([row['Latitude'], row['Longitude']],
	                        radius=0.3,
	                        fill_color="#D3D3D3",
	                       ).add_to(m)
	stationArr = crime_truncated[['Latitude', 'Longitude']].to_numpy()

	# plot heatmap
	m.add_children(plugins.HeatMap(stationArr, radius=15))
	m


################## Pull Together ####################


def go(df, type_ = "HOMICIDE"):
	crime_truncated = read_data(df, type_)
	heat_map(crime_truncated)
