# import packages and data section
import folium
import numpy as np
import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from DataSource.dataSource import *
import json, requests
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from SPARQLWrapper import SPARQLWrapper2
from dash import html
import json, requests
from SPARQLWrapper import SPARQLWrapper2


# this url used to call foursquare API with explore endpoint
url = 'https://api.foursquare.com/v2/venues/explore?'
# foursquare Places API user authentication
client_id = 'QCLYU41XGKCAAEXJIMGC3QHRK2MQDT3VNRIL4KP4JYOMGRZX',
client_secret = 'IKTOYX0OGSQRFQCPTKG4ETTN3PJB1RTRBGDLXLJ1QOI3UVT4',
# convert average_crime type to integer
crime_location["average_crime"] = crime_location["average_crime"].astype('int')
# this used to build boundaries between London's regions
crime_scale = list(np.linspace(crime_location["average_crime"].min(),
                          crime_location["average_crime"].max(),
                          5, dtype=int))
crime_scale[-1] = crime_scale[-1]+1

# create an alert object when the user inter max_price less than the min_price
price_alert = dbc.Alert("The minimum price should be less than the maximum price!", dismissable=True, color="danger"),


## CALLBACK CODE SECTION ##
## Callbacks help to build functions on dash

# The embassyInfo Callback helps the application to get the country name from the drop down list
# then return Embassy information
# The output of the function will be return to Div object with ID= embassy-info in the layout.py.
# The input of this callback comes from the drop-down object with ID = embassy in layout.py.
@app.callback(Output("embassy-info", "children"),
              [Input("embassy", "value")]
             )
def embassyInfo(embassy):
    # filter the dataframe based on the selected country
    df = Embassy[Embassy["country"] == embassy]
    # this empty list is created in order to store a card with all embassy info
    emb = []
    # append a card of embassy info to the ebm list then return it and sent it to div box with ID embassy-info
    # in the layout.py file.
    emb.append(dbc.Card(html.Div([
            html.H4(df["Embassy_name"], className="card-title, text-success"),
            html.Div("Contact number: " + df["contact_number"]),
            html.Div("Address: " + df["address"]),
            html.Div("Email: " + df["email"]),
            html.Div("Website: " + df["website"]),
        ], ), color="light", outline=True), ),
    return emb

# update_figure callback function allow the app to take all the criteria that the user selected to filter properties
# on th map.
# Output 1: map, to display the map on the Iframe object in layout.py file.
# Output 2: price_alert, to sent an alert message to the user when the min price is greater than the max price.
# the output2 will be display in Div object with id= price_alert in layout.py file.
# All the callback inputs comes from objects in layout.py file, there IDs are neighbourhood, property_type, bedrooms,
# Min_price and Max_price.
# Input 1: neighbourhood, allows the user to select a neighbourhood.
# Input 2: property_type, allows the user to select property_type.
# Input 3: bedrooms, allows the user to select number of bedrooms.
# Input 4: Min_price, allows the user to set the min price.
# Input 5:Max_price , Allows the user to set the max price.
@app.callback([Output('map', 'srcDoc'),
              Output("price_alert", "children")],
              [Input('neighbourhood', "value"),
               Input("property_type", "value"),
               Input("bedrooms", "value"),
               Input("Min_price", "value"),
               Input("Max_price", "value")
               ])
def update_figure(neighbourhood, property_type,bedrooms, Min_price, Max_price):
    # convert dropdown values into lists to allow the system filter the dataset by using isin() function.
    neighbourhood = list(neighbourhood)
    property_type = list(property_type)
    bedrooms = list(bedrooms)

    # comparing between Min and Max price values to send an alert message in case the min value is greater than the
    # max value, and DO NOT return any map marker.
    if  Min_price > Max_price :
        return dash.no_update, price_alert
    else:
    #If the user inserts a max price with a value greater than the min the filtered properties will be shown on the map.
        london_map = folium.Map(location=[51.509865, -0.118092], zoom_start=11) #London boundaries
        # choropleth object is created to draw boundaries of regions.
        choropleth = folium.Choropleth(
            geo_data=london_geo,
            data=crime_location,
            columns=['SNTBoroughName', 'average_crime'],
            key_on='feature.properties.LAD13NM',
            threshold_scale=crime_scale,
            fill_color='YlGnBu',
            fill_opacity=0.2,
            line_opacity=0.5,
            legend_name="Crime rate per month",
            reset=True
        )
        # remove legend
        for key in choropleth._children:
            if key.startswith('color_map'):
                del (choropleth._children[key])
        choropleth.add_to(london_map)
        # filter the dataset based on the selected criteria.
        df = listing[
            (listing['neighbourhood_cleansed'].isin(neighbourhood)) &
            (listing["property_type"].isin(property_type)) &
            (listing["bedrooms"].isin(bedrooms)) &
            (listing["price"].isin(range(Min_price, Max_price)))
        ]
        df.reset_index(drop=True, inplace=True)
        # create a marker on the map for each property in df dataframe.
        for i in (range(len(df))):
            lat = df["latitude"][i]
            long = df["longitude"][i]

            folium.Marker(location=[lat, long], popup=" <img src=" + df["picture_url"][i] +
                        " height=150 width=250> <b>name: </b>" + df["name"][i] +
                        "<br> <b>accommodates: </b> " + str(df["accommodates"][i]) +
                        "<br> <b>Bedrooms: </b> " + str(df["bedrooms"][i]) +"<br> <b>Price: </b> " +
                        str(df["price"][i]) +" &pound;"+ "<br><b>Listing link: </b><a href=' "+ df["id_test"][i]+
                        " ' target='_blank' > click here</a> " ,external_link=True,
                          icon=folium.Icon(color= df["color"][i], icon='home')).add_to(london_map)
        # save the created map in html file
        london_map.save("london_map.html")
        return open('london_map.html', 'r',  encoding="utf8").read(), dash.no_update

# foodVenue_page is created in order to build pages for food venues (Breakfast, Lunch, Dinner, and cafe)
# this function allows the user to filter places based on diet type
# Output: foodVenue_page is the ID of Div object in layout.py, this object will contains the output of this Callback,
# which is a food venue page.
# Input 1:  DietType, is a value comes from a dropdown list (allows the user to filter places based on the diet type)
# Input 2: property-data, it is dcc.Store object is used to pass data from one page to another here we pass (lat, long)
# of selected property in order to pass them  into foursquare API to find nearby places.
# Input3: meal-data. it is dcc.Store object stores the selected meal (Breakfast, Lunch, Dinner, and cafe)
# from the property page.
@app.callback([Output("foodVenue_page", "children")],
              [Input('DietType', "value"),
               Input('property-data', 'data'),
               Input('meal-data', 'data')]
              )
def foodVenue_page(DietType,data, meal):
    # ll object is created to store lat and long in the same format of foursquare API ("lat, long")
    ll = (str(data[0][0]) +","+ str(data[1][0]))
    def venue():
        # this part of the code  is a foursquare API call to get the venue data.
        params = dict(
            client_id= client_id,
            client_secret= client_secret,
            v='20210923', # the v parameter is a date in YYYYMMDD format.
            ll= ll,       # latitude and longitude
            radius=500,   # area around the place 500 meters
            query= meal,  # query is type of meal (Breakfast, Lunch, Dinner, and cafe)
            limit=50,     #number of calls
        )
        resp = requests.get(url=url, params=params)
        data = json.loads(resp.text)
        # These empty lists are created in order to store the extracted data from foursquare API
        Venue_Name =[]
        distance = []
        category =[]
        Venue_Location =[]
        # Extracting data from foursquare API
        for venue in range(len(data["response"]["groups"][0]["items"])):
            Venue_Name.append(data["response"]["groups"][0]["items"][venue]["venue"]["name"])
            distance.append(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["distance"])
            category.append(data["response"]["groups"][0]["items"][venue]["venue"]['categories'][0]["shortName"])
            Venue_Location.append(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["formattedAddress"])
        # The dataframe is created to store all the extracted data into one data structure.
        data = pd.DataFrame({"Venue_Name": Venue_Name,
                             "distance": distance,
                             "category": category ,
                             "Venue_Location": Venue_Location })
        return data
    data = venue()

    def venue_foursquare_filtered(df, data):
        # These empty lists are created in order to store the extracted data from foursquare API and their
        # matches information form London_restaurants dataset
        name = []
        distance = []
        cuisines = []
        avg_rating = []
        address = []
        category = []
        i = 0
        while i < len(df):
            for j in range(len(data)):
                # fuzz.partial_ratio is used to calculate the similarities between venue names and their addresses.
                # from two data sources to link them together.
                venue_name = fuzz.partial_ratio(df["restaurant_name"][i], data["Venue_Name"][j])
                if venue_name > 80 :
                   venue_lcation = fuzz.partial_ratio(df["address"][i], str(data["Venue_Location"][j]))
                   if venue_lcation >= 50:
                   #when it finds similarities between names and addresses
                   # it will append necessary info into the empty lists.
                        name.append(df["restaurant_name"][i])
                        distance.append(data["distance"][j])
                        cuisines.append(df["cuisines"][i])
                        avg_rating.append(df["avg_rating"][i])
                        address.append(str(data["Venue_Location"][j][:2]))
                        category.append(data["category"][j])

            i = i + 1
        # The dataframe is created to store all the extracted data into one data structure.
        filtered_foodVenues = pd.DataFrame({"name":name,"category":category,"cuisines":cuisines, "address":address,
                                            "distance":distance, "avg_rating":avg_rating}).drop_duplicates(subset=['address'])
        # sort the venue data by distance from nearest to farthest venues.
        filtered_foodVenues.sort_values(by = 'distance', inplace=True)
        filtered_foodVenues.reset_index(drop=True, inplace=True)
        # if there is no venue nearby the user the system should shows this message "Sorry, there is no matching place!"
        if len(filtered_foodVenues) == 0:
            return [html.H4("Sorry, there is no matching place!",className="card-title text-success text-center")]
        # if the is one or more venues nearby the user, the application should list them to the user
        else:
            # this list is created to store cards with all venue information
            venue_list = []
            for i in range(len(filtered_foodVenues)):
                venue_list.append(dbc.Card(html.Div([
                    html.H4(filtered_foodVenues['name'][i], className="card-title, text-success"),
                    html.Div(str(filtered_foodVenues['category'][i])),
                    html.Div("Cuisines: " + str(filtered_foodVenues['cuisines'][i])),
                    html.Div("Address: " + str(filtered_foodVenues['address'][i][1:-1])),
                    html.Div("Distance: " + str(filtered_foodVenues['distance'][i]) + " m"),
                    html.Div("Rating: " + str(filtered_foodVenues['avg_rating'][i])),
                ], ), style={"width": "30.5rem"}, ), ),
            return [venue_list]

    # If the user selects a specific diet type then the dataset will be filtered based on the diet type.
    if DietType in["Vegetarian", "Vegan", "Gluten_free"]:
        DietType = [DietType]
        df = London_restaurants[(London_restaurants[DietType[0]] == "Y")]
        df.reset_index(drop=True, inplace=True)
        return venue_foursquare_filtered(df, data)
    # If the user does not care about the diet type and select (Any type) the dataset will not be filtered.
    if DietType == "Any type":
        df = London_restaurants
        return venue_foursquare_filtered(London_restaurants, data)
    # If the user not select any value from the dropdown list, the application will return empty page.
    else:
        return [""]



############## Train callback #########################
# Output: Train_page is a div object in layout.py is created to display data about train.
# Input:  train-data is dcc.Store object is used to pass data from one page to another here we pass (lat, long) of
# selected property in order to pass them  into foursquare API to find nearby train station.
@app.callback([Output("Train_page", "children")],
              [Input('train-data', 'data'),]
              )
def train_page(data):
    # ll object is created to store lat and long in the same format of foursquare API ("lat, long")
    ll = (str(data[0][0]) + "," + str(data[1][0]))
    def train():
        # this part of the code  is a foursquare API call to get the venue data.
        params = dict(
            client_id=client_id,
            client_secret=client_secret,
            v='20210923', # the v parameter is a date in YYYYMMDD format
            ll= ll,  # latitude and longitude
            radius=800,  # area around the place 800  meters
            query='Train Station',
            limit= 50,
        )
        resp = requests.get(url=url, params=params)
        data = json.loads(resp.text)
        # These empty lists are created in order to store the extracted data from foursquare API
        name = []
        distance = []
        address = []
        category = []
        # Extracting data from foursquare API
        for venue in range(len(data["response"]["groups"][0]["items"])):
            if data["response"]["groups"][0]["items"][venue]["venue"]['categories'][0]["shortName"] == "Train Station":
                name.append(data["response"]["groups"][0]["items"][venue]["venue"]["name"])
                address.append(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["formattedAddress"])
                distance.append(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["distance"])
                category.append(data["response"]["groups"][0]["items"][venue]["venue"]['categories'][0]["shortName"])
        # The dataframe is created to store all the extracted data into one data structure.
        data = pd.DataFrame({"name":name, "distance":distance, "address": address,"category":category})
        return data
    # store data from foursquare API in data object
    data = train()
    # store underground data in df object
    df = underground_stations
    def train_underground(df, data):
        # These empty lists are created in order to store the extracted data from foursquare API and their
        # matches information form underground_stations dataset
        name = []
        distance = []
        line = []
        address = []
        category = []

        for j in range(len(data)):
            for i in range(len(df)):
                # fuzz.partial_ratio is used to calculate similarity between train station names from
                # underground_stations dataset and data from foursquare API in order to link them together
                venue_name = fuzz.partial_ratio(df["station"][i], data["name"][j])
                if venue_name > 70:
                    # append all necessary data into the above empty lists
                    name.append(str(data["name"][j]))
                    distance.append(str(data["distance"][j]))
                    line.append(str(df["line"][i]))
                    address.append(str(data["address"][j][:2]))
                    category.append(str(data["category"][j]))
        # If there is no nearby train station, the application will send a message says
        # "Sorry, there is no Train station near you!"
        if len(name) == 0:
            return [html.H4("Sorry, there is no Train station nearby!", className="card-title text-success text-center")]
        # If there is one or more train satation nearby the selected property, the app will return the train station
        # name, category, line, address and the distance between the train station and the selected property.
        else:
            venue_list = []
            for i in range(len(name)):
                venue_list.append(dbc.Card(html.Div([
                    html.H4(str(name[i]), className="card-title, text-success"),
                    html.Div(str(category[i])),
                    html.Div("line: " + str(line[i])),
                    html.Div("Address: " + str(address[i][1:-1])),
                    html.Div("Distance: " + str(distance[i]) + " m"),
                ], ), style={"width": "30.5rem"}, ), ),
            return [venue_list]

    return train_underground(df, data)

############## bus callback #########################
# Output: Bus_page is a div object created to display data about bus stops.
# Input:  bus-data is dcc.Store object is used to pass data from one page to another here we pass (lat, long) of
# selected property in order to pass them  into foursquare API to find nearby bus stops.
@app.callback([Output("Bus_page", "children"),],
              [Input('bus-data', 'data'),]
              )
def bus_page(data):
    # ll object is created to store lat and long in the same format of foursquare API ("lat, long")
    ll = (str(data[0][0]) + "," + str(data[1][0]))

    def bus():
        # this part of the code  is a foursquare API call to get the venue data.
        params = dict(
            client_id=client_id,
            client_secret=client_secret,
            v='20210923', # the v parameter is a date in YYYYMMDD format
            ll= ll,  # latitude and longitude
            radius=500,  # area around the place 800 meters
            query='bus stop',
            limit=50
        )
        resp = requests.get(url=url, params=params)
        data = json.loads(resp.text)
        # These empty lists are created in order to store the extracted data from foursquare API
        name = []
        distance = []
        address = []
        category = []
        # Extracting data from foursquare API
        for venue in range(len(data["response"]["groups"][0]["items"])):
            name.append(data["response"]["groups"][0]["items"][venue]["venue"]["name"])
            address.append(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["formattedAddress"])
            distance.append(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["distance"])
            category.append(data["response"]["groups"][0]["items"][venue]["venue"]['categories'][0]["shortName"])
        # If there is no bus stop nearby the selected property, the system will show a message says
        # "Sorry, there is no Bus Stop near you!"
        if len(name) == 0:
            return [html.H4("Sorry, there is no Bus Stop nearby!", className="card-title text-success text-center")]
        # If there is one or more bus stops nearby the selected property, the app will return the bus stop name,
        # address and the distance between the train station and the selected property.
        else:
            venue_list = []
            for i in range(len(name)):
                venue_list.append(dbc.Card(html.Div([
                    html.H4(str(name[i]), className="card-title, text-success"),
                    html.Div(str(category[i])),
                    html.Div("Address: " + str(address[i][1:-1])),
                    html.Div("Distance: " + str(distance[i]) + " m"),
                ], ), style={"width": "30.5rem"}, ), ),

            return [venue_list]
    return bus()



##### ACtivities Callback #######
# Output: activity_page is a div object created to display data about activities.
# Input:  activity-data is dcc.Store object is used to pass data from one page to another here we pass (lat, long) of
# selected property in order to pass them  into foursquare API to find nearby activities.
@app.callback([Output("activity_page", "children")],
              [Input('activity-data', 'data'),]
              )
def activity_page(data):
    ll = (str(data[0][0]) + "," + str(data[1][0]))
    def things_to_do():
        params = dict(
            client_id=client_id,
            client_secret=client_secret,
            v='20210923', # the v parameter is a date in YYYYMMDD format
            ll=ll,  # latitude and longitude
            radius=1000,  # area around the place in meters
            query='things to do',
            limit=50
        )
        resp = requests.get(url=url, params=params)
        data = json.loads(resp.text)
        # activity is an empty list to store activity venue names.
        activity = []
        # activity_info is an empty list to store information about the activity.
        activity_info = []
        for venue in range(len(data["response"]["groups"][0]["items"])):
            # extract the venue name from foursquare API and replace spaces with underscores to pass
            # the name into dbpedia API.
            activity.append(str(data["response"]["groups"][0]["items"][venue]["venue"]["name"]).replace(" ", "_"))
            # for each nearby activity venue the application will link it with information about it. The information
            # about the activity venue comes from dbpedia API.
        for venue in range(len(activity)):
            venue_name = activity[venue]
            sparql = SPARQLWrapper2("http://dbpedia.org/sparql")
            sparql.setQuery("""
            SELECT ?label ?thumbnail
            WHERE {
                <http://dbpedia.org/resource/""" + venue_name + """>
                    dbo:abstract ?label ; 
                    dbo:thumbnail ?thumbnail .
                FILTER (lang(?label) = 'en')
            }
            """)

            for result in sparql.query().bindings:

                if (result["label"].value != []):
                    activity_info.append(result["label"].value)
            # These empty lists are created in order to store the extracted data from foursquare API
            Venue_Name = []
            Venue_Location = []
            distance = []
            category = []
            for venue in range(len(data["response"]["groups"][0]["items"])):
                Venue_Name.append(str(data["response"]["groups"][0]["items"][venue]["venue"]["name"]))
                Venue_Location.append(
                    str(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["formattedAddress"]))
                distance.append(str(data["response"]["groups"][0]["items"][venue]["venue"]["location"]["distance"]))
                category.append(
                    str(data["response"]["groups"][0]["items"][venue]["venue"]['categories'][0]["shortName"]))
            # The dataframe is created to store all the extracted data into one data structure.
            data = pd.DataFrame({"Venue_Name": Venue_Name, "Venue_Location": Venue_Location, "distance": distance,
                                 "category": category})

            # These empty lists are created in order to store the extracted data from foursquare API and their
            # matches information form dbpedia API.
            Venue_Name = []
            Venue_Location = []
            distance = []
            category = []
            info = []

            for j in range(len(data)):
                for i in range(len(activity_info)):
                    # fuzz.partial_ratio is used to calculate similarity between venue names from
                    # dbpedia API and foursquare API in order to link them together
                    venue_name = fuzz.partial_ratio(activity_info[i], data["Venue_Name"][j])
                    if venue_name > 50:
                        Venue_Name.append(str(data["Venue_Name"][j]))
                        distance.append(str(data["distance"][j]))
                        info.append(str(activity_info[i]))
                        Venue_Location.append(str(data["Venue_Location"][j][:2]))
                        category.append(str(data["category"][j]))
                # if there is no activity venue nearby the selected property, the app will show a messages says
                # "Sorry, there is no Activity near you!"
                if len(Venue_Name) == 0:
                    return [html.H4("Sorry, there is no Activity nearby!",
                                    className="text-success text-center mb-4 font-weight-normal")]
                # if there is one or more activities nearby the selected property, the app will display all venues with
                # venue name,category, address, info and distance.
                else:
                    venue_list = []
                    for i in range(len(Venue_Name)):
                        venue_list.append(dbc.Card(html.Div([
                            html.H4(str(Venue_Name[i]), className="card-title, text-success"),
                            html.Div(str(category[i])),
                            html.Div("Address: " , className="text-success"),
                            html.Div(str(Venue_Location[i][1:-1])),
                            html.Div("Info: ", className="text-success"),
                            html.Div(str(info[i])),
                            html.Div("Distance: ", className="text-success"),
                            html.Div(str(distance[i]) + " m"),
                        ], ), style={"width": "50rem"}, ), ),


                    return [venue_list]
    return things_to_do()