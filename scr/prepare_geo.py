import pandas as pd
import altair as alt
import geopandas as gpd
import json
from shapely.geometry import Point, Polygon
import shapely.wkt

geojson_path = '../data/vancouver.geojson'
van_json = json.loads(open(geojson_path).read())

for a in van_json['features']:
    if(a['properties']['Name'] == 'Downtown'):
        a['properties']['Name'] = 'Central Business District'
    elif(a['properties']['Name'] == 'Arbutus-Ridge'):
        a['properties']['Name'] = 'Arbutus Ridge'
        
data_path = '../data/crimedata_csv_all_years.csv'
van_pd = pd.read_csv(data_path)

van_pd_less = van_pd.query('NEIGHBOURHOOD == NEIGHBOURHOOD & NEIGHBOURHOOD != "Musqueam" & NEIGHBOURHOOD != "Stanley Park"')
van_pd_less_neighborhood = set(van_pd_less['NEIGHBOURHOOD'].unique())

geojson_filepath = '../data/our_geojson.geojson'

with open(geojson_filepath, 'w') as our_geojson:
    json.dump(van_json, our_geojson)
    
def open_geojson(path):
    """
    Opens a geojson file at "path" filepath
    """
    with open(path) as json_data:
        d = json.load(json_data)
    return d

def get_geopandas_df(path):
    """
    Creates geopandas dataframe from geeojson file 
    at "path" filepath
    """
    open_json = open_geojson(path)
    gdf = gpd.GeoDataFrame.from_features((open_json))
    return gdf

# Create geopandas dataframe from Central Park geoJson file
gdf = get_geopandas_df(geojson_filepath)
gdf = gdf.rename(columns = {'Name': 'NEIGHBOURHOOD'}).drop(columns = 'description')