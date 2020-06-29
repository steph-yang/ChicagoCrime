import pandas as pd
import numpy as np
import string
import us
import geopandas as gpd
import jellyfish
import warnings
warnings.filterwarnings('ignore')
import plotly.figure_factory as ff
import plotly.graph_objects as go
import censusdata
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from matplotlib import pyplot as plt


############## Use 2017 as Example ###################


year = 2017


############## Read in Excel Data  ###################

def read_crime_data(year):
    '''
    Read in crime data
    '''
    # Read in data from xls
    df = eval('pd.read_excel("{}.xls")'.format(year))
    
    # Remove empty columns and rows
    df = df.dropna(axis=1, how='all').dropna(thresh=3)
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    df["State"] = df["State"].fillna(method='ffill')
    df = df.fillna(0)
    df = df.reset_index(drop=True)
    
    # Rename columns
    df = df.loc[:, df.columns.notnull()]
    for c in df.columns:
        new_c = c
        if "\n" in c:
            new_c = c[:c.index("\n")]
        new_c = new_c.translate(str.maketrans('', '', string.punctuation))
        new_c = new_c.translate(str.maketrans('', '', string.digits))
        df = df.rename(columns={c: new_c})
        
    # Add column for all crime types
    df["Total"] = df["Violent"] + df["Property"] + df["Arson"]
    
    # Add State abbr column
    state = us.states.mapping('name', 'abbr')
    state = {k.upper():v for k,v in state.items()}
    df["State"] = df["State"].map(lambda x: x.translate(str.maketrans('', '', string.digits)))
    df["City"] = df["City"].map(lambda x: x.translate(str.maketrans('', '', string.digits)))
    df["state_id"] = df["State"].map(lambda x: state[x])
    
    return df


############## Reconcile State and City, Add fips Code  ###################


def merge_fips(df):
    '''
    Merge crime with city Fips
    '''
    cities = pd.read_csv("uscities.csv")
    cities = cities.astype({'city': 'str', "state_id":"str", "county_name":"str", "county_fips":"str"})
    df = df.merge(cities[["county_name", "county_fips", "state_id", "city"]], left_on=['state_id','City'],\
         right_on = ["state_id", "city"], how='left', left_index=False)
    df = df.drop(["city"], axis = 1)
    df = df.rename(columns={"county_name":"county", "county_fips":"fips"})
    df["fips"] = df["fips"].apply(lambda x: str(x).zfill(5))
    return df


############## Calculate Crime Rate by Type  ###################


def calculate_crime_rate(df, columns):
    '''
    Calculate crime rate based on column names
    '''
    for c in columns:
        new_c = "{}_rate".format(c)
        df[new_c] = df[c]*100000/df["Population"]
    return df


############## Match Fuzzy City Names and Remove NA  ###################


def check_nan(df):
    '''
    Match fuzzy city names
    '''
    cities = pd.read_csv("uscities.csv")
    cities = cities.astype({'city': 'str', "state_id":"str", "county_name":"str", "county_fips":"str"})   
    
    df_fuzzy = df[df.fips == "00nan"]
    df_tuple = list(zip(df_fuzzy.state_id, df_fuzzy.City, df_fuzzy.index))
    cities_tuple = list(zip(cities.state_id, cities.city, cities.county_fips))
    
    rv = []
    for d in df_tuple:
        for c in cities_tuple:
            if c[0] == d[0]:
                if jellyfish.jaro_distance(c[1], d[1]) >= 0.85 or c[1] in d[1]\
                    or d[1] in c[1]:                
                    df.loc[df.index==d[2], ['City']] = c[1]
                    df.loc[df.index==d[2], ['fips']] = c[2]
                    break
        else:
            df = df.drop(d[2])
    return df
