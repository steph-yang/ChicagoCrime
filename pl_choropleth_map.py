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

import read_FBI_data

#################################

year = 2017

############## Use Read_FBI_Data ###################


def read_data(year):
    '''
    Import functions from read_FBI_data and read
    in data
    Input:
	year: int, 2010~2018
    Output: df
    '''
    df = read_FBI_data.read_crime_data(year)
    df = read_FBI_data.merge_fips(df)
    df = read_FBI_data.calculate_crime_rate(df, ["Violent", "Property", "Total", "Rape"])
    df = read_FBI_data.check_nan(df)
    return df


############## Interactive Choropleth Map (County level) ###################


def plot_rate_county(df, year):
    '''
    Create County-level choropleth map
    '''
    colorscale = ["#deebf7", "#d2e3f3", "#c6dbef", "#b3d2e9", "#9ecae1",
        "#85bcdb", "#6baed6", "#57a0ce", "#4292c6"
    ]

    endpts = list(np.linspace(1000, 5000, len(colorscale) - 1))
    fips = df['fips'].tolist()
    values = df['Total_rate'].tolist()

    fig = ff.create_choropleth(
        fips=fips, values=values, scope=['usa'],
        binning_endpoints=endpts, colorscale=colorscale,
        show_state_data=False,
        show_hover=True,
        asp = 2.9,
        title_text = 'Crime Rate by County in Year {}'.format(year),
        legend_title = 'Crime Rate per 100k Population'
    )
    
    fig.layout.template = None
    fig.show()
    plt.savefig('by_county.png')


##############  Interactive Choropleth Map (State level) ###################

def plot_rate_state(df, year, col):
    '''
    Create State-level interactive map
    '''
    # Group by counties into state
    state_df = df.groupby(["State", "state_id"]).agg({k:"sum" for k in \
				["Population", "Violent", "Property", "Total", "Rape"]}).reset_index()
    state_df = calculate_crime_rate(state_df, ["Violent", "Property", "Total", "Rape"])

    # Plot
    fig = go.Figure(data=go.Choropleth(
        locations=state_df['state_id'], # Spatial coordinates
        z = state_df[col].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Rate per 100,000 population",
    ))

    fig.update_layout(
        title_text = '{} by State in {}'.format(col, year),
        geo_scope='usa', # limite map scope to USA
    )
    fig.show()
    plt.savefig('by_state.png')


##############  Pull Together ###################

def go(year):
    df = read_data(year)
    plot_rate_county(df, year)
    plot_rate_state(df, year, "Total_rate")

	
