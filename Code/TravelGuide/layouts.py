# import packages and data section
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash_daq as daq
from DataSource.dataSource import listing, Embassy

############## Layout of mainpage/map ######################
layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Where do you want to stay in London?",
                        className='text-success text-center mb-4 font-weight-normal'), width=12)
    ),
    dbc.Row([
        # Map legend
    html.Ul([
        html.Li("📍 Low crime rate", style={'color': 'green', 'text-indent': '20px'}),
        html.Li("📍 Middle crime rate", style={'color': 'orange', 'text-indent': '20px'}),
        html.Li("📍 High crime rate", style={'color': 'red', 'text-indent': '20px'})
        ],
        ),
        dbc.Col([
            # neighbourhood Dropdown menu
            dcc.Dropdown(id='neighbourhood', clearable=False,
                         options=[{'label': str(b), 'value': b} for b in
                                  sorted(listing.neighbourhood_cleansed.unique())],
                         value="neighbourhood",
                         placeholder="Neighbourhood",
                         multi=True
                         ),
            # property types Dropdown menu
            dcc.Dropdown(id='property_type', clearable=False,
                         options=[{'label': str(b), 'value': b} for b in sorted(listing.property_type.unique())],
                         value="property_type",
                         placeholder="Property type",
                         multi=True
                         ),
            #number of bedrooms Dropdown menu
            dcc.Dropdown(id='bedrooms',
                         options=[{'label': str(b), 'value': b} for b in sorted(listing.bedrooms.unique())],
                         value="bedrooms",
                         placeholder="Number of Bedroom",
                         multi=True,
                         ),
            html.Br(),
            # Price (Max and Min) Input fields
            dbc.Row([
                html.Div(id="price_alert", children=[]),
                dbc.Col([
                    # the price range per night (Min and Max prices)
                    daq.NumericInput(
                        label='Minimum price per night',
                        id='Min_price',
                        min=0,
                        max=100000,
                        value=0,
                        size=100
                    ),
                ],),
                dbc.Col([
                    daq.NumericInput(
                        label='Maximum price per night',
                        id='Max_price',
                        min=0,
                        max=100000,
                        value=0,
                        size=100
                    ),
                ],),
            ], ),
        #Embassies Dropdown list
        html.Br(),
        html.H6("Embassy info",className='text-success mb-4 font-weight-normal'),
        dcc.Dropdown(id='embassy',
                     options=[{'label': str(b), 'value': b} for b in sorted(Embassy["country"].unique())],
                     value="embassy",
                     placeholder="Select your country"),
        html.Br(),
        # This div object will contain the output of the callback.
        html.Div(id="embassy-info"),
        ],),
        # Iframe is used to contains the map
        dbc.Col([
            dbc.Spinner(
            # This Iframe object will contain the output of the callback (Map).
            html.Iframe(id='map',
                        srcDoc=None,
                        width='100%',
                        height='600'),),

        ], width={'size': 8},),
    ],),

], fluid=True)

############## Layout of property ######################
def prop_layout(df):

    card_main = dbc.Card([
            dbc.Row([
                dbc.Col([
                        # property image
                        dbc.CardImg(src=df["picture_url"],
                                    top=True, # even though this property value is True, the image display in the
                                              # middle of the first column.
                                    alt=listing['name']),

                    ],),
                    dbc.Col([
                        dbc.CardBody([
                                # property name
                                html.H4(df['name'],className="card-title, text-success"),
                                dbc.Row([
                                    dbc.Col([
                                        # button to navigate the user to property page in Airbnb website
                                        dbc.Button("Click to see it in Airbnb", color="success", size="sm",
                                                   outline=True,
                                                   className="me-1",
                                                   href=df['listing_url'],
                                                   external_link=True),
                                    ], width={'size': 3}), ]),
                                # paragraph tag to contains property description
                                html.P(
                                    # remove html tags and other samples.
                                    df['description'].str.replace(r'<[^<>]*>', '', regex=True),
                                    className="card-text",
                                ),
                                html.H6("Location:", className="card-subtitle, text-success"),
                                # paragraph tag to contains property address/location
                                html.P(
                                    df["neighbourhood"],
                                    className="card-text",
                                ),
                                html.H6("Neighborhood overview:", className="card-subtitle, text-success"),
                                # paragraph tag to contains property neighborhood overview
                                html.P(
                                    df["neighborhood_overview"].str.replace(r'<[^<>]*>', '', regex=True),
                                    className="card-text",
                                ),
                                html.H6("About Host:", className="card-subtitle, text-success"),
                                # paragraph tag to contains information about the host
                                html.P(df["host_about"], className="card-text"),
                                # paragraph tag to contains property Review Score (Negative, Positive, and Neutral)
                                html.H6(html.P("Review Score: "+ df["review_scores_location"]),
                                                className="card-subtitle, text-success"),
                                html.Br(),
                                # the bar graph here to show summary data about the comments of property
                                html.H6("What other people think about this property:",
                                        className="card-subtitle, text-success"),
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(
                                            figure={
                                                'data': [
                                                     {'x': ['Negative', 'Neutral', 'Positive'],
                                                      'y': [int(df['neg']*100),
                                                            int(df['neu']*100) ,
                                                            int(df["pos"]*100)],
                                                      'type': 'bar',
                                                      'color': 'green'},
                                                ],
                                                'layout': {
                                                    'xaxis': {
                                                        'title': 'Review types'
                                                    },
                                                    'yaxis': {
                                                        'title': 'Average Number of reviews'
                                                    },
                                            },},
                                        )
                                     ], width={'size': 4}),

                                           ], ),
                                # dcc.Store is used to store the data in browser session to pass the data (lat,long)
                                # from one page to another.
                                dcc.Store(id='property-data', data=[], storage_type='memory'), # 'local' or 'session'
                                # This section of the page allows the user to select a nearby place he wants to visit.
                                dbc.Row([html.H6(html.P("Nearby places:"), className="card-subtitle, text-success"),
                                         dbc.Col([
                                             # the Breakfast button
                                         dbc.Button("Breakfast",
                                                    color="success",
                                                    size="sm",
                                                    outline=True,
                                                    className="me-1",
                                                    href=df['id_test']+"/"+"Breakfast",
                                                    external_link=True),
                                         ], width={'size': 1}),

                                         dbc.Col([
                                             # the Lunch button
                                             dbc.Button("Lunch",
                                                        color="success",
                                                        size="sm",
                                                        outline=True,
                                                        className="me-1",
                                                        href=df['id_test']+"/"+"Lunch",
                                                        external_link=True),
                                         ], width={'size': 1}),

                                         ], ),

                                html.Br(),
                                dbc.Row([
                                    dbc.Col([
                                        # the Dinner button
                                        dbc.Button("Dinner",
                                                   color="success",
                                                   size="sm",
                                                   outline=True,
                                                   className="me-1",
                                                   href=df['id_test']+"/"+"Dinner",
                                                   external_link=True),
                                    ], width={'size': 1}),
                                    dbc.Col([
                                        # the Cafe button
                                        dbc.Button("Cafe",
                                                   color="success",
                                                   size="sm",
                                                   outline=True,
                                                   className="me-1",
                                                   href=df['id_test']+"/"+"Cafe",
                                                   external_link=True),
                                    ], width={'size': 1}),]),

                                html.Br(),
                                dbc.Row([
                                         dbc.Col([
                                             # Activities Button
                                             dbc.Button("Activities",
                                                        color="success",
                                                        size="sm",
                                                        outline=True,
                                                        className="me-1",
                                                        href=df['id_test']+"/"+"activity",
                                                        external_link=True),
                                         ], width={'size': 1}),
                                         ], ),
                                html.Br(),
                                # This section of the page allows the user to select train or bus nearby the property.
                                html.H6("Nearby public transportation:", className="card-subtitle, text-success"),
                                html.Br(),
                                dbc.Row([
                                    dbc.Col([
                                        # train button
                                        dbc.Button("Train",
                                                   color="success",
                                                   size="sm",
                                                   outline=True,
                                                   className="me-1",
                                                   href=df['id_test']+"/"+"Train",
                                                   external_link=True),
                                    ], width={'size': 1}),

                                    dbc.Col([
                                        # bus button
                                        dbc.Button("Bus",
                                                   color="success",
                                                   size="sm",
                                                   outline=True,
                                                   className="me-1",
                                                   href=df['id_test']+"/"+"Bus",
                                                   external_link=True),
                                    ], width={'size': 1}),
                                ], ),

                            ]
                        ), ],
                        className="col-md-8",
                    ),
                ], className="g-0 d-flex align-items-center",
            )
        ],
        className="mb-3",
    )
    property_layout = html.Div([
        dbc.Row([dbc.Col(card_main, width=11.5), ], justify="around"), ])
    return property_layout

###### venue_food layout (Breakfast, Lunch, Dinner, and Cafe) #############
def venue_food(lat,long, meal):
    # cafe button does not carry the correct query which is Coffee
    # this if statement will check the meals if it cafe, then it will convert it to coffee.
    if meal == "Cafe":
        meal = "Coffee"
    else:
        meal= meal
    layout2 = dbc.Container([
        # dcc.Store to store data (lat, long, and meal type) in the browser session
        dcc.Store(id='property-data', data=[lat,long], storage_type='memory'),
        dcc.Store(id='meal-data', data= meal, storage_type='memory'),
        # page title
        dbc.Row(
            dbc.Col(html.H1("Where do you want to have your " + meal +"?",
                            className='text-success text-center mb-4 font-weight-normal'), width=12)
        ),
        dbc.Row([
            dbc.Col([

                # Diet type Dropdown menu
                dbc.Spinner(
                dcc.Dropdown(id='DietType', clearable=False,
                             options=[{'label': str(b), 'value': b} for b in ["Vegetarian", "Vegan", "Gluten_free","Any type"]],
                             value="Diet Type",
                             placeholder="Select Diet Type",
                             ),),

            # div here is used to containded data that retrived from the callback function
            # spinner is used to tell the user about data loading
            dbc.Spinner(
            html.Div(id="foodVenue_page"), color='success', fullscreen=True,
            ),
            ], width={'size': 4, "offset": 4}),
        ],
        ),
    ], fluid=True)
    return layout2

###################### Train layout ######################
def Train(lat,long):
    layout3 = dbc.Container([
        # dcc.Store to store data (lat, long) in the browser session
        dcc.Store(id='train-data', data=[lat,long], storage_type='memory'),
        dbc.Row(
            dbc.Col(html.H1("The nearby Train stations",
                            className='text-success text-center mb-4 font-weight-normal'), width=12)
        ),
        dbc.Row([
            dbc.Col([
                # div here is used to containded data that retrived from the callback function
                dbc.Spinner(
                html.Div(id="Train_page"), color='success', fullscreen=True),
            ] , width={'size': 4, "offset": 4}),],),
    ], fluid=True)
    return layout3

###################### Bus layout ######################
def Bus(lat,long):
    layout4 = dbc.Container([
        # dcc.Store to store data (lat, long) in the browser session
        dcc.Store(id='bus-data', data=[lat,long], storage_type='memory'),
        dbc.Row(
            dbc.Col(html.H1("The nearby Bus stops",
                            className='text-success text-center mb-4 font-weight-normal'), width=12)
        ),
        dbc.Row([
            dbc.Col([
            # div here is used to containded data that retrieved from the callback function
                dbc.Spinner(
             html.Div(id="Bus_page"), color='success', fullscreen=True)
            ] , width={'size': 4, "offset": 4}),],),

    ], fluid=True)
    return layout4

###################### Activities layout ######################
def activity(lat,long):
    layout5 = dbc.Container([
        # dcc.Store to store data (lat, long) in the browser session
        dcc.Store(id='activity-data', data=[lat,long], storage_type='memory'),
        dbc.Row(
            dbc.Col(html.H1("The nearby Activities ",
                            className='text-success text-center mb-4 font-weight-normal'), width=12)
        ),
        dbc.Row([
            dbc.Col([
                # div here is used to contained data that retrieved from the callback function
                dbc.Spinner(
                html.Div(id="activity_page"), color='success', fullscreen=True)
            ] , width={'size': 4, "offset": 4}),],),

    ], fluid=True)
    return layout5