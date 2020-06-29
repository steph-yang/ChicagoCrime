# ChicagoCrime

## Introduction

<p>		This research aims at reevaluating public safety problem in Chicago, more specifically, identifying key features behind blocks with high crime rate and devising public policy solutions accordingly. In most social science literature, demographics are known to exhibit strong correlations with crime; yet, we believe demographics alone are not sufficient to explain this complex issue. Therefore alongside traditional demographics,we introduce two newgroups – infrastructure and traffic flow – to better capture neighborhood characteristics.. </p><br>

<p>		Three types of machine learning techniques are used in this research: unsupervised clustering, supervised regression, and synthetic control method. In unsupervised learning, we apply hierarchical clustering and K-means to select states shared similar demographic features with Illinois. Then, scope is narrowed down to Chicago in the supervised regression part in order to key factors behind its high crime rate. Lastly, we constructed a simulated Chicago using synthetic control method with data of real cities selected from unsupervised learning. This method helps us better understand results of a policy or project.</p>

## Data Source

In this project, we use three data sources:
1. Crime data:  FBI Offenses Known to Law Enforcement - Crime in the U.S. Archive, including 2010~2018<br>
Data downloaded from <https://ucr.fbi.gov/crime-in-the-u.s>
2. ACS data: Demographic features <br>
Data retrieved via Census API as: [API]<https://www.census.gov/data/developers/data-sets/acs-1year.html>
3. Census tract boundaries: Census tract for Chicago
4. Property Value: <https://www.experian.com/blogs/ask-experian/research/median-home-values-by-state/>
5. State-County-City Match: From government website
6. Taxi Trips: From [Chicago Data Portal]<https://data.cityofchicago.org/>

## Directory
1. Data: This folder is where we store all the data. <br>
**Notice**: this is an empty filefolder, but all data can be found via links above.
2. Notebooks:
	1. Descriptive_heatmap

		1. Function for Heatmap of criminal incidences locations in Chicago
		![](readmepic/1.png)

	2. Unsupervised_Cluster (for selecting States with similar demographic features with Illinois)

		1. Function for by-county crime rate plotting
		
		![](readmepic/2.png)

		2. Function for by-state crime rate plotting
		
		![](readmepic/3.png)

		3. Hierarchical Clustering
		
		![](readmepic/4.png)

		4. K-means Clustering
		
		![](readmepic/5.png)

	3. Supervised_And_Synth include linear regression model and synthetic control method.

		1. Linear model construction
		
		![](readmepic/6.png)

		2. Model Regularization
		
		![](readmepic/7.png)
		
		3. Bootstrapping
		4. Synth Method
3. STATA: This folder include the do files showing the further statistical analysis for Bootstrapping and Synthetic Control Method.
4. Excel: This folder include the xlsx files we use to draw our trends.
5. PDFs: Final presentation and Final report.
