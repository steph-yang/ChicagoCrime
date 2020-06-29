import pandas as pd
from sodapy import Socrata
import censusdata
import geopandas as gpd
import numpy as np


import matplotlib.pyplot as plt
%matplotlib inline

import warnings
warnings.filterwarnings('ignore')


################ Set Variable #####################

code = {"s6ha-ppgi":["units","sum", "affordable_units"],
        "4u6w-irs9":["","size","grocery_num"],
        "x8fc-8rcq":["", "size","library_count"],
        "sj6t-9cju":["", "size", "arts_count"],
        "z8bn-74gv":["","size","police_count"],
        "7nii-7srd":["", "size", "abandoned_house"],
        "hec5-y4x5":["", "size", "graffiti_count"],
        "pfsx-4n4m":["total_passing_vehicle_volume", "sum", "traffic_sum"]}


################ Retrieve Facility Data via API #####################

def get_blockgroups():
    '''
    Read blockgroup data via API
    '''
    client = Socrata("data.cityofchicago.org", None)

    neighborhood = gpd.read_file("https://data.cityofchicago.org/resource/bt9m-d2mf.geojson?$limit=9999999")
    neighborhood["geoid10"] = neighborhood["geoid10"].map(lambda x: str(x)[:12])
    blockgroups = neighborhood.dissolve(by='geoid10')[['geometry']].reset_index()
    return blockgroups



def retrieve_gov_data(code):
    '''
    Retrieve facility data via API
    Input:
        code: dict
    '''
    df = blockgroups
    
    for k,v in code.items():
        col = v[0]
        method = v[1]
        
        gdf = gpd.read_file("https://data.cityofchicago.org/resource/{}.geojson?$limit=9999999".format(k))
        gdf = gdf.dropna(subset=["geometry"])
        print(str(col)+" downloaded!")

        gdf = gpd.tools.sjoin(blockgroups, gdf, how="inner", op='intersects')
        
        if col:
            gdf = gdf.astype({col: 'int32'})
            group = gdf.groupby(['geoid10'])[col].sum().to_frame().reset_index()
        else:
            group = gdf.groupby(['geoid10']).size().to_frame().reset_index()
        
        df = pd.merge(df, group, on="geoid10", how="outer")
        print(str(col)+" merged!")
    
    df.fillna(0, inplace=True)
    df.columns = ["geoid", "geometry"] + [v[2] for v in code.values()]
    return df


################ Choropleth Map within Chicago #####################

def map_plot(df, col, color = 'Blues'):
    fig, ax = plt.subplots(1, 1)
    vmin, vmax = 0, df[col].quantile(0.75)
    df.plot(column=df[col],ax = ax, cmap=color, legend=True, \
           norm=plt.Normalize(vmin=vmin, vmax=vmax))
    plt.title('{}'.format(col))
    plt.axis('off')
    plt.show()
    print(df[col].describe())


################ Pull Together #####################

def go(code):
    blockgroups = get_blockgroups()

    # This line takes about 20 mins to run.
    df = retrieve_gov_data(code)
    map_plot(df, 'graffiti_count', "OrRd")
    map_plot(df, 'abandoned_house', "OrRd")

