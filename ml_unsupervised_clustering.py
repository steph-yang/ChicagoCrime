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
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import pl_choropleth_map.py

#################################

year = 2017

############# Retrieve Census Data via API ####################

def read_acs_data():
    '''
    Read in census data via censusdata api
    '''
    census_tables = {
        'B02001_001E': 'Race Total', 
        'B02001_002E': 'White', 
        'B02001_003E': 'Black', 
        'B19013_001E': 'Median Income',
        'B01002A_001E': "White_Age",
        'B01002B_001E': "Black_Age"}
    keys = list(census_tables.keys())
    acs_df = censusdata.download('acs5', 
               2018,
               censusdata.censusgeo([('state', '*')]),
               keys)
    acs_df.rename(columns=census_tables, inplace=True)
    acs_df["black_pct"] = acs_df["Black"]/acs_df["Race Total"]
    acs_df["white_pct"] = acs_df["White"]/acs_df["Race Total"]
    acs_df["age"] = (acs_df["White_Age"]+acs_df["Black_Age"])/2
    acs_df = acs_df.reset_index()
    acs_df["State"] = acs_df["index"].apply(lambda x: str(x)[:str(x).index(":")])
    acs_df = acs_df[["State", "Median Income", "black_pct", "white_pct", "age"]]
    return acs_df


############# Read Property Value Data ####################


def read_property(acs_df):
    '''
    Read and clean state property value data
    '''
    property_value = pd.read_csv("property.csv")[["State", "Median Home Value"]]
    property_value["Median Home Value"] = property_value["Median Home Value"]\
                                    .apply(lambda x: int(''.join(c for c in x if c.isdigit())))
    property_value = property_value.merge(acs_df, left_on=["State"],\
	         right_on = ["State"], how='left', left_index=False)
    property_value["State"] = property_value["State"].str.upper()
    return property_value


############# Merge Dataset ####################


def merge_data(property_value, state_df):
    full_cluster = property_value.merge(state_df[["Violent_rate", "Property_rate", \
						"Total_rate", "State", "state_id"]],
	                                left_on=["State"], right_on = ["State"], how='left', \
	                                left_index=False)
    full_cluster = full_cluster[["Median Home Value", "Median Income","black_pct",\
	                         "white_pct", "Violent_rate", "Property_rate", "Total_rate",\
	                         "State", "state_id", "age"]]
    full_cluster = full_cluster.set_index(["State", "state_id"])
    full_cluster = full_cluster[["Median Income", "black_pct", "white_pct","age"]]
    return full_cluster


############# Hierarchical Clustering ####################


def hierarchy_dendrogram(full_cluster):
    '''
    Apply hierarchical clustering method and visualize results
    '''
    Z = linkage(full_cluster, 'ward')
    fig = plt.figure(figsize=(25, 6))
    dendrogram(Z, labels = full_cluster.index, leaf_rotation=90)
    plt.axhline(linestyle='--', y=30000) 
    plt.xlabel("States", fontsize = 25)
    plt.xticks(fontsize=15)
    plt.title("Ward Clustering for States based on Demographic Features", fontsize = 25)
    plt.show()

def hierarchy_table(full_cluster):
    '''
    Apply hierarchical clustering methods and store results in df
    '''
    Z = linkage(full_cluster, 'ward')
    fl = fcluster(Z,3,criterion='maxclust')
    cl_table = full_cluster.reset_index()
    cl_table = cl_table[["state_id"]]
    cl_table["group"] = fl.tolist()
    cl_table = cl_table.groupby(["group"])["state_id"].apply(lambda x: ', '.join(x.astype(str))).reset_index()
    return cl_table


############# K_means Clustering ####################


def k_means(full_cluster):
    '''
    Apply hierarchical clustering methods
    '''
    k_data = full_cluster[["age", "Median Income", "black_pct"]]
    kmeans = KMeans(n_clusters=3, random_state=0).fit(k_data)
    return kmeans

def k_means_table(kmeans):
    '''
    Store k-means clustering results in df
    '''
    pd.set_option('display.max_colwidth', -1)
    k_data["group"] = kmeans.labels_.tolist()
    k_table = k_data.reset_index()
    k_table = k_table[["group", "state_id"]].set_index(["group"]).sort_index()
    k_table = k_table.groupby(["group"])["state_id"].apply(lambda x: ', '.join(x.astype(str))).reset_index()
    return k_table


def k_means_3D(kmeans):
    '''
    Visualize k-means results in 3D plot
    '''
    center = kmeans.cluster_centers_
    k_data["group"] = kmeans.labels_.tolist()

    fig = plt.figure(figsize=(20, 6))

    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

    labels = kmeans.labels_

    ax.scatter(k_data["age"], k_data["Median Income"], k_data["black_pct"],
	           c=labels.astype(np.float), zorder = 1, s=50)

    x = k_data["age"].tolist()
    y = k_data["Median Income"].tolist()
    z = k_data["black_pct"].tolist()
    l = [i[1] for i in k_data.index]

    for i in range(len(l)):
        label = l[i]
	ax.text(x[i], y[i], z[i]+0.02, '%s' % (label), size=8.5, zorder=1, color='k')
	    
    for i, c in enumerate(center):
	ax.scatter(c[0], c[1], c[2], color = "red",s=120, marker = "^")
	ax.text(c[0]+0.2, c[1]+1000, c[2]-0.05, 'Center {}'.format(i+1), size=15, color='grey')
	    
    ax.w_xaxis.set_ticklabels([])
    ax.w_yaxis.set_ticklabels([])
    ax.w_zaxis.set_ticklabels([])
    ax.set_xlabel('age', fontsize=20)
    ax.set_ylabel('Median Income', fontsize=20)
    ax.set_zlabel('black_pct', fontsize=20)
    ax.set_title('K-means Clustering of States based on Demographic Features', fontsize=20)
    # ax.dist = 12
    plt.show()


############# Cross Search ####################


def cross_check(df1, df2, state):
    g1 = df1[df1['state_id'].str.contains(state)]["state_id"].tolist()[0].split(", ")
    g2 = df2[df2['state_id'].str.contains(state)]["state_id"].tolist()[0].split(", ")
    return list(set(g1).intersection(g2))


############# Pull Together ####################


def go(year):
    # Group counties into state
    df = read_data(year)
    state_df = df.groupby(["State", "state_id"]).agg({k:"sum" for k in \
    			["Population", "Violent", "Property", "Total", "Rape"]}).reset_index()
    state_df = calculate_crime_rate(state_df, ["Violent", "Property", "Total", "Rape"])
    acs_df = read_acs_data()
    property_value = read_property(acs_df)
    full_cluster = merge_data(property_value, state_df)

    # hierarchy
    cl_table= hierarchy_table(full_cluster)
    hierarchy_dendrogram(full_cluster)

    # k-means
    kmeans = kmeans(full_cluster)
    k_means_3D(kmeans)
    k_table = k_means_table(kmeans)

    rv = cross_check(k_table, cl_table)

    return rv
