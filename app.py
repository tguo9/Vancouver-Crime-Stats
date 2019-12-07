import pandas as pd
import altair as alt
import geopandas as gpd
import json
from shapely.geometry import Point, Polygon
import shapely.wkt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np

app = dash.Dash(__name__, assets_folder='assets')
app.config['suppress_callback_exceptions'] = True
server = app.server

app.title = 'Vancouver Crime Stats'

df = pd.read_csv('data/crimedata_csv_all_years.csv')
df = df.query('NEIGHBOURHOOD == NEIGHBOURHOOD & NEIGHBOURHOOD != "Musqueam" & NEIGHBOURHOOD != "Stanley Park"')
df['DATE'] = pd.to_datetime({'year':df['YEAR'], 'month':df['MONTH'], 'day':df['DAY'], 'hour':df['HOUR']})
df['DAY_OF_WEEK_NAME'] = pd.DatetimeIndex(df['DATE']).day_name()
dofw = pd.DataFrame({'DAY_OF_WEEK_NAME': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 'DAY_OF_WEEK': [1,2,3,4,5,6,7]})
df = pd.merge(df, dofw, how="left", on="DAY_OF_WEEK_NAME")

list_of_locations = df['NEIGHBOURHOOD'].dropna().unique()
list_of_locations = np.insert(list_of_locations, 0, 'ALL')
list_of_crimes = df['TYPE'].unique()
list_of_crimes = np.insert(list_of_crimes, 0, 'ALL')
list_of_years = ['YEAR', 'MONTH', 'DAY_OF_WEEK', 'HOUR']

def plot_by_neighbor(year_init = 2010, year_end = 2018, neighbourhood="ALL", crime = "ALL", time_scale = "YEAR"):
    """
    Create line chart plot of neighbourhood specific crime data

    Parameters
    ----------
    year_init : int (default 2010)
        start year of data set
    year_end : int (default 2018)
        ending year of data set
    neighbourhood : str (default 'ALL')
        neighbourhood to examine
    crime : str (default 'ALL')
        crime type to examine
    time_scale : str (default 'YEAR')
        time scale of line graph

    Returns
    -------
    chart : altair.Chart object
        altair line chart with filtered crime data
    """
    df_line = df.query('@year_init <= YEAR & YEAR <= @year_end')
    
    if neighbourhood != "ALL":
        if crime != "ALL":
            df_line = df_line.query('TYPE == @crime & NEIGHBOURHOOD == @neighbourhood').groupby([time_scale]).count().reset_index()
        else:    
            df_line = df_line.query('NEIGHBOURHOOD == @neighbourhood').groupby([time_scale]).count().reset_index()
    else:
        neighbourhood = 'All Neighbourhoods'
        if crime != "ALL":
            df_line = df_line.query('TYPE == @crime').groupby([time_scale]).count().reset_index()
        else:
            crime = 'All Crimes'
            df_line = df_line.groupby([time_scale]).count().reset_index() 
    
    chart = alt.Chart(df_line).mark_line().encode(
        alt.X(time_scale+':N'),
        alt.Y('TYPE:Q', title='Number of Crimes'),
        alt.Color(value="blue")
    ).configure(
        background='#f7e0bc' #HEX color code
    ).configure_axisX(
        labelAngle=45,
        grid=True
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=15
    ).configure_title(
        fontSize=15
    ).properties(
    height=300,
    width=500,
    title= neighbourhood + ': ' + crime
    )
    return chart


def get_geopandas_df(path):
    """
    Create a geopandas dataframe from the geeojson at the specified filepath
    """
    with open(path) as json_data:
        open_json = json.load(json_data)
    gdf = gpd.GeoDataFrame.from_features(open_json)
    return gdf

geojson_filepath = 'data/our_geojson.geojson'
gdf = get_geopandas_df(geojson_filepath)
gdf = gdf.rename(columns = {'Name': 'NEIGHBOURHOOD'}).drop(columns = 'description')

def plot_choropleth(year_init = 2010, year_end = 2018, crime_type = 'all', crime_threshold = 1):
    """
    Create choropleth of crime data across neighbourhoods in Vancouver

    Parameters
    ----------
    year_init : int (default 2010)
        start year of data set
    year_end : int (default 2018)
        ending year of data set
    crime_type : str (default 'ALL')
        crime type to examine
    crime_threshold : float
        maximum value of choropleth color scale

    Returns
    -------
    altair.Chart object
        altair choropleth chart with filtered crime data
    """
    crime_cnt = (df.query('@year_init <= YEAR & YEAR <= @year_end').groupby(['NEIGHBOURHOOD', 'TYPE'])[['MINUTE']]
                .count().rename(columns = {'MINUTE': 'COUNT'})
                .reset_index())

    if(crime_type.lower() == 'all'):
        crime_type = 'All Crimes'
        crime_cnt = crime_cnt.groupby('NEIGHBOURHOOD')[['COUNT']].sum().reset_index()
    else:
        crime_cnt = crime_cnt.query('TYPE == @crime_type').groupby('NEIGHBOURHOOD')[['COUNT']].sum().reset_index()

    crime_cnt['MINMAX'] = (crime_cnt['COUNT'] - crime_cnt['COUNT'].min()) / (crime_cnt['COUNT'].max() - crime_cnt['COUNT'].min())
    crime_cnt['MINMAX'] = round(crime_cnt['MINMAX'], 3)
    crime_geo_cnt = gdf.merge(crime_cnt, on = 'NEIGHBOURHOOD')

    alt_json = json.loads(crime_geo_cnt.to_json())
    alt_base = alt.Data(values = alt_json['features'])

    base_map = alt.Chart(alt_base, 
                        title = f"Crime Type = {crime_type}").mark_geoshape(
            stroke='white',
            strokeWidth=1
        ).encode(
            tooltip = [alt.Tooltip('properties.NEIGHBOURHOOD:N', title =  'Neighbourhood'), 
                    alt.Tooltip('properties.COUNT:Q', title = 'Count'), 
                    alt.Tooltip('properties.MINMAX:Q', title =  'Ratio')]
        ).properties(
            width=1000,
            height=600
        )

    choro = alt.Chart(alt_base).mark_geoshape(
        fill = 'lightgray', 
        stroke = 'white'
    ).encode(
        alt.Color('properties.MINMAX:Q', 
                legend = alt.Legend(title = 'Crime Index'), 
                scale=alt.Scale(domain = (0.0, crime_threshold),
                                range = ('#CAFFA8', '#DF3F12', '#000000')
                                )
                )
    )

    return (choro + base_map).configure_title(fontSize=15).properties(width = 700, height = 400)


app.layout = html.Div([

    # Header
    html.Div([
        html.Img(src='https://img.icons8.com/wired/64/000000/policeman-male.png', style={'float':'left', 'margin-top': '10px', 'margin-left': '8px'}),
        html.H1('Vancouver Crime Stats', style={'float':'left', 'margin-left':'15px'}),
        html.Div(["Open source crime data from the City of Vancouver shown for neighbourhood comparison"], style={'position':'absolute', 'float':'left', 'margin-top': '60px', 'margin-left':'90px'})
    ],style={'position':'absolute', 'width':'96%', 'height':'90px', 'backgroundColor':'#9ee6f6', 'border': '3px solid black'}),
    
    # Crime Map
    html.Div([
        
        html.Div([
            html.H3('Crime Type'),
            dcc.Dropdown(
            id='crime-chart',
            options=[
                {'label': i, 'value': i}
                for i in list_of_crimes
            ],
            value = 'ALL',
            placeholder = 'ALL',
            style=dict(width='80%',
                verticalAlign="middle"
                )
            ),

            html.H3('Years to Include'),
            html.Div([
                dcc.RangeSlider(
                    id='year-slider',
                    min=df['YEAR'].min(),
                    max=df['YEAR'].max(),
                    step=1,
                    marks={i:'{}'.format(i) for i in range(df['YEAR'].min(),df['YEAR'].max()+1,2)},
                    value=[df['YEAR'].min(), df['YEAR'].max()]
                ),
            ], style={'width': '60%', 'margin-left':'20px'}),

        ], style={'height':'200px', 'margin-left':'20px'}),

        html.Div([
            html.Iframe(
                sandbox='allow-scripts',
                id = 'choropleth',
                height='500',
                width='80%',
                style={'border-width': '0', 'float':'left'},
                srcDoc=plot_choropleth().to_html()
            ),

            html.Div([
                html.H4('Crime Index Max'),
                dcc.Slider(
                    id='slider-updatemode',
                    marks={'0.1': '0.1', '1': '1'},
                    max=1,
                    min=0.1,
                    value=1,
                    step=0.01,
                    updatemode='drag',
                    vertical=True
                ),
            ], style={'height': '200px', 'float':'left', 'margin-left': '30px', 'margin-top': '10px'}),
        ])

    ], style={'float': 'left', 'width': '60%', 'height':'800px', 'margin-top': '93px', 'background-color': '#e0e0eb', 'border': '3px solid black'}),
    
    # Crime Trends
    html.Div([

        html.Div([
            html.H3('Neighbourhood'),
            dcc.Dropdown(
            id='dd-chart',
            options=[
                {'label': i, 'value': i}
                for i in list_of_locations
            ],
            value = 'ALL',
            placeholder = 'ALL',
            style=dict(width='90%',
                verticalAlign="middle"
                )
            ),

            html.H3('Time Scale'),
            dcc.Dropdown(
            id='year-chart',
            options=[
                {'label': i, 'value': i}
                for i in list_of_years
            ],
            value = 'YEAR',
            style=dict(width='90%',
                verticalAlign="middle"
                )
            ),

        ], style={'height':'200px', 'margin-left':'20px'}),
        
        html.Iframe(
            sandbox='allow-scripts',
            id='plot',
            height='500',
            width='95%',
            style={'border-width': '0', 'margin-left':'20px'},
            srcDoc=plot_by_neighbor().to_html()
        ),
        
    ], style={'float': 'left', 'width': '36.5%', 'height':'800px', 'margin-top': '93px', 'backgroundColor':'#e0e0eb', 'border': '3px solid black'}),        
])

@app.callback(
    dash.dependencies.Output('plot', 'srcDoc'),
    [dash.dependencies.Input('year-slider', 'value'), dash.dependencies.Input('dd-chart', 'value'), dash.dependencies.Input('crime-chart', 'value'), dash.dependencies.Input('year-chart', 'value')])
def update_plot(year_range, location, types, year):

    updated_plot = plot_by_neighbor(year_init=year_range[0], year_end=year_range[1], neighbourhood=location, crime=types, time_scale=year).to_html()

    return updated_plot

@app.callback(
    dash.dependencies.Output('choropleth', 'srcDoc'),
    [dash.dependencies.Input('year-slider', 'value'), 
    dash.dependencies.Input('crime-chart', 'value'), 
    dash.dependencies.Input('slider-updatemode', 'value')])
def update_choropleth(year_range, crime_type, crime_threshold):

    updated_plot = plot_choropleth(year_init=year_range[0], 
                                    year_end=year_range[1], 
                                    crime_type=crime_type, 
                                    crime_threshold=crime_threshold).to_html()

    return updated_plot

if __name__ == '__main__':
    app.run_server(debug=True)