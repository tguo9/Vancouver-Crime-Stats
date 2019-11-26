import pandas as pd
import altair as alt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, assets_folder='assets')
app.config['suppress_callback_exceptions'] = True
server = app.server

app.title = 'Vancouver Crime Stats'

df = pd.read_csv('../data/crimedata_csv_all_years.csv')

list_of_locations = df['NEIGHBOURHOOD'].dropna().unique()
dict_of_locations = dict(zip(list_of_locations, list_of_locations))

list_of_crimes = df['TYPE'].dropna().unique()
dict_of_crimes = dict(zip(list_of_crimes, list_of_crimes))

def plot_by_neighbor(neighbourhood="ALL", crime = "Theft of Bicycle", time_scale = "YEAR"):
    if neighbourhood != "ALL":
        if crime != "ALL":
            df_line = df.query('TYPE == @crime & NEIGHBOURHOOD == @neighbourhood').groupby([time_scale]).count().reset_index()
        else:    
            df_line = df.query('NEIGHBOURHOOD == @neighbourhood').groupby([time_scale]).count().reset_index()
    else:
        if crime != "ALL":
            df_line = df.query('TYPE == @crime').groupby([time_scale]).count().reset_index()
        else:
            df_line = df.groupby([time_scale]).count().reset_index() 
    
    chart = alt.Chart(df_line).mark_line().encode(
        alt.X(time_scale+':N'),
        alt.Y('TYPE:Q', title='Number of Crimes'),
        alt.Color(value="blue")
    ).configure_axisX(
        labelAngle=90,
        grid=True
    ).configure(
        background='#f7e0bc' #HEX color code
    ).properties(
    height=300,
    width=500,
    title=crime
    )
    return chart

app.layout = html.Div([

    html.H1('Vancouver Crime Stats'),
    html.Img(src='https://img.icons8.com/wired/64/000000/policeman-male.png'),
    html.H2('Here is our first plot:'),
    html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        height='600',
        width='625',
        style={'border-width': '0'},

        ################ The magic happens here
        srcDoc=plot_by_neighbor().to_html()
        ################ The magic happens here
        ),

        dcc.Dropdown(
        id='dd-chart',
        options=[
            {'label': i, 'value': i}
            for i in list_of_locations
        ],
        value = 'ALL',
        style=dict(width='45%',
            verticalAlign="middle"
            )
        ),

        dcc.Dropdown(
        id='crime-chart',
        options=[
            {'label': i, 'value': i}
            for i in list_of_crimes
        ],
        value = 'Theft of Bicycle',
        style=dict(width='45%',
            verticalAlign="middle"
            )
        ),
])

@app.callback(
    dash.dependencies.Output('plot', 'srcDoc'),
    [dash.dependencies.Input('dd-chart', 'value'), dash.dependencies.Input('crime-chart', 'value')])
def update_plot(location, types):

    updated_plot = plot_by_neighbor(neighbourhood=location, crime=types).to_html()

    return updated_plot

if __name__ == '__main__':
    app.run_server(debug=True)