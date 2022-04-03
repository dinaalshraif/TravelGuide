import sqlite3
import pandas as pd
# create a connection with the database
con = sqlite3.connect('DataSource/TravelGuide.db')
# load the data from database tables into pandas DataFrames
listing = pd.read_sql_query("SELECT * from listing", con)
# Data Sources of listing: 1- http://insideairbnb.com/get-the-data.html
#                          2- https://data.london.gov.uk/dataset/mps-hate-crime-or-special-crime-dashboard-data
Embassy = pd.read_sql_query("SELECT * from embassy", con)
# Data Source of Embassy: https://www.gov.uk/government/publications/foreign-embassies-in-the-uk
crime_location = pd.read_sql_query("SELECT * from crime", con)
# Data Source of crime_location: https://data.london.gov.uk/dataset/mps-hate-crime-or-special-crime-dashboard-data
London_restaurants = pd.read_sql_query("SELECT * from London_restaurants", con)
# Data Source of London_restaurants: https://www.kaggle.com/stefanoleone992/tripadvisor-european-restaurants-eda/data
underground_stations = pd.read_sql_query("SELECT * from underground_stations", con)
# Data Source of underground_stations: https://tfl.gov.uk/info-for/open-data-users/our-open-data#on-this-page-2

# Read geojson file
london_geo = r'DataSource/LondonBoroughsBoundries.geojson'
# Data Source of london_geo: https://martinjc.github.io/UK-GeoJSON/