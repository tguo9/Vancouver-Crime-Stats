import pandas as pd
import altair as alt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, assets_folder='assets')
server = app.server

app.title = 'Dash app with pure Altair HTML'

df = pd.read_csv('data/crimedata_csv_all_years.csv')
df = df.query('YEAR >= 2014').drop(columns = ['HUNDRED_BLOCK', 'X', 'Y'], inplace = False)
def plot_by_neighbor(df, col1, col2, xtitle, ytitle, color):
    df_new = (df.query('TYPE == \'{}\' | TYPE ==\'{}\''.format(col1, col2))
                .groupby('NEIGHBOURHOOD')
                .count()
                .reset_index())
    cnt_max = df_new['TYPE'].max()

    return alt.Chart(df_new).mark_bar().encode(
        alt.X('TYPE:Q', title = xtitle),
        alt.Y('NEIGHBOURHOOD:N', 
            sort = alt.EncodingSortField(
                field = 'TYPE', 
                order = 'descending'), 
            title = ytitle), 
        color = alt.condition(
            alt.datum.TYPE == cnt_max, 
            alt.value(color), 
            alt.value('grey'))
    )

app.layout = html.Div([

    html.H1('This is my first dashboard'),
    html.H2('This is a subtitle'),

    html.H3('Here is our first plot:'),
    html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        height='450',
        width='625',
        style={'border-width': '0'},

        ################ The magic happens here
        srcDoc=plot_by_neighbor(df, 'Theft of Vehicle', 'Theft from Vehicle', 'Count of vehicle related crimes', 'Neighbourhood', 'orange').to_html()
        ################ The magic happens here
        ),
])

if __name__ == '__main__':
    app.run_server(debug=True)