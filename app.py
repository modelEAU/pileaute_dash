import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import Dateaubase
import PlottingTools

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
cursor, conn = Dateaubase.create_connection()

app.layout = html.Div(children=[
    html.H1(children=dcc.Markdown('pil*EAU*te Dashboard')),
    dcc.Interval(id='refresh_interval', interval=60 * 1000, n_intervals=0),
    html.Div(children='''
        Graph example (tries to update every 60 seconds)
    '''),

    dcc.Graph(id='example_graph')
])


@app.callback(
    Output('example_graph', 'figure'),
    [Input('refresh_interval', 'n_intervals')])
def draw_example_graph(n):
    try:
        _, conn = Dateaubase.create_connection()
    except Exception:
        raise PreventUpdate
    Start = Dateaubase.date_to_epoch('2017-09-01 12:00:00')
    End = Dateaubase.date_to_epoch('2017-10-01 12:00:00')
    Location = 'Primary settling tank effluent'
    Project = 'pilEAUte'
    param_list = ['COD', 'CODf', 'NH4-N', 'K']
    equip_list = ['Spectro_010', 'Spectro_010', 'Ammo_005', 'Ammo_005']

    extract_list = {}
    for i in range(len(param_list)):
        extract_list[i] = {
            'Start': Start,
            'End': End,
            'Project': Project,
            'Location': Location,
            'Parameter': param_list[i],
            'Equipment': equip_list[i]
        }
    df = Dateaubase.extract_data(conn, extract_list)
    fig = PlottingTools.extract_plotly(df)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
