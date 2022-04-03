## You Must Run This File to Run The APPLICATION ##

# import modules, functions and files
from os import path
from dash import html
from app import app
from DataSource.dataSource import listing
from layouts import *
from dash import dcc
from dash.dependencies import Input, Output
import callbacks


# This is the main layout of the application, all the layouts in the layout.py will be
# presented in the Div component that has id='page-content'
# the structure of the code from https://dash.plotly.com/urls
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# This part of the code will update the layout depend on the URL
# For each layout read the current URL page "http://127.0.0.1:5000/pagename" and return the layout
@app.callback(Output('page-content', 'children'), #update the  page content
              [Input('url', 'pathname')]) # read the page URL

def display_page(pathname):
    # Split the URL to extract the page name/number
    pathname = pathname.split("/")
    # open map page
    if pathname[-1] == '':
        return layout
    # open food venues pages
    if pathname[-1] == "Breakfast" or pathname[-1] =="Lunch" or pathname[-1] =="Dinner" or pathname[-1] =="Cafe":
        df = listing[(listing['id_test'].isin([pathname[-2]]))]
        latitude = df["latitude"]
        longitude = df["longitude"]
        # the latitude and longitude will be passed to Foursquare places API, "ll" parameter to find
        # the nearby food venues, the data will be passed via object called dcc.Store in the layout.py
        # then use it as an input in callback.py.
        # pathname[-1] is the meal name in the URL, will be passed to the "query" parameter in Foursquare places API.
        return venue_food(latitude, longitude, pathname[-1])
    # open train page
    if pathname[-1] =="Train":
        #Extracting latitude and longitude from the listing table where pathname[-2] contains the property ID
        # from its URL.
        df = listing[(listing['id_test'].isin([pathname[-2]]))]
        latitude = df["latitude"]
        longitude = df["longitude"]
        # the latitude and longitude will be passed to Foursquare places API to find the nearby train station
        # the data will be passed via object called dcc.Store in the layout.py then use it as an input in callback.py.
        return Train(latitude,longitude)
    # open bus page
    if pathname[-1] == "Bus":
        df = listing[(listing['id_test'].isin([pathname[-2]]))]
        latitude = df["latitude"]
        longitude = df["longitude"]
        # the latitude and longitude will be passed to Foursquare places API to find the nearby bus stops
        # the data will be passed via object called dcc.Store in the layout.py then use it as an input in callback.py.
        return Bus(latitude, longitude)
    # open activity page
    if pathname[-1] == "activity":
        df = listing[(listing['id_test'].isin([pathname[-2]]))]
        latitude = df["latitude"]
        longitude = df["longitude"]
        # the latitude and longitude will be passed to Foursquare places API to find the nearby activity venue
        # the data will be passed via object called dcc.Store in the layout.py then use it as an input in callback.py.
        return activity(latitude, longitude)
    # open property page
    if int(pathname[-1]) in listing.id_test:
        pathname = [pathname[-1]] # pathname is property ID taken from the URL.
        df = listing[(listing['id_test'].isin(pathname))] # Extracting property data
        return prop_layout(df)
    else:
         return '404' #If page not found return 404

#server runs at http://127.0.0.1:5000/
if __name__ == '__main__':
    app.run_server(port=5000,debug=True)

