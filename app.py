from datetime import datetime, timedelta, timezone

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.io as pio

import Dateaubase
import PlottingTools

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
pio.templates.default = "plotly_white"

NEW_DATA_INTERVAL = 30  # in seconds
DAYS_OF_DATA = 1
STORE_MAX_LENGTH = DAYS_OF_DATA * 24 * 60 * 60  # worst-case of sensor that updates every second


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        dcc.Store(id='avn-db-store'),
        html.H1(children=dcc.Markdown('pil*EAU*te Dashboard')),
        dcc.Interval(id='refresh-interval', interval=NEW_DATA_INTERVAL * 1000, n_intervals=0),
        html.Div(
            children='''Graph example (tries to update every 60 seconds'''
        ),
        dcc.Graph(id='example-graph', animate=True)
    ]
)


@app.callback(
    Output('avn-db-store', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def store_data(n, data):
    try:
        _, conn = Dateaubase.create_connection()
    except Exception:
        raise PreventUpdate
    print('level 0')
    end = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    three_days_ago = datetime.now(timezone.utc) - timedelta(days=DAYS_OF_DATA)
    if not data:
        print('level 1')
        start = datetime.strftime(three_days_ago, '%Y-%m-%d %H:%M:%S')
    else:
        print('level 2')
        stored_df = pd.read_json(data)
        print('what is the latest time?')
        print(pd.to_datetime(list(stored_df.index)[-1]))
        last_time = pd.to_datetime(list(stored_df.index)[-1])
        print(f'the type is {type(last_time)}')
        
        if last_time < three_days_ago:
            print('level 3')
            start = datetime.strftime(three_days_ago, '%Y-%m-%d %H:%M:%S')
        else:
            print('level 4')
            start = datetime.strftime(last_time, '%Y-%m-%d %H:%M:%S')
    print('level 0b')
    Project = 'pilEAUte'
    Location = [
        'Primary settling tank effluent',
        'Pilote effluent',
        'Pilote effluent',
        'Pilote reactor 5'
    ]
    equip_list = [
        'Ammo_005',
        'Varion_002',
        'Varion_002',
        'FIT-430'
    ]
    param_list = [
        'NH4-N',
        'NH4-N',
        'NO3-N',
        'Flowrate (Gas)',
    ]
    extract_list = {}
    for i in range(len(param_list)):
        extract_list[i] = {
            'Start': Dateaubase.date_to_epoch(start),
            'End': Dateaubase.date_to_epoch(end),
            'Project': Project,
            'Location': Location[i],
            'Parameter': param_list[i],
            'Equipment': equip_list[i]
        }

    new_df = Dateaubase.extract_data(conn, extract_list)
    length_new = len(new_df)
    if not data:
        print('level 5')
        complete_df = new_df
    elif length_new == 0:
        print('level 6')
        raise PreventUpdate
    else:
        print('level 7')
        # print(f'trying to concat dataframes. New df has {length_new} lines')
        complete_df = pd.concat([stored_df, new_df], sort=True)
        complete_df = complete_df.iloc[length_new:]
    print('level 0c')
    json_data = complete_df.to_json(date_format='iso')
    return json_data


@app.callback(
    Output('example-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def example_graph(data):
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        fig = PlottingTools.extract_plotly(df)
        print('fig has been drawn')
        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
