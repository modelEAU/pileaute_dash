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

DATABASE_NAME = 'dateaubase2020'
LOCAL_SERVER = r'GCI-PR-DATEAU02\DATEAUBASE'
NEW_DATA_INTERVAL = 30  # in seconds
DAYS_OF_DATA = 1
MINUTES_OF_DATA = 300
new_constant = 42
STORE_MAX_LENGTH = DAYS_OF_DATA * 24 * 60 * 60  # worst-case of sensor that updates every second


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        dcc.Interval(id='refresh-interval', interval=NEW_DATA_INTERVAL * 1000, n_intervals=0),
        dcc.Store(id='avn-db-store'),
        html.Div(
            children=[
                html.Img(
                    src='assets/flowsheetPilEAUte_with_logo.png',
                    style={'align': 'middle'}
                ),
            ],
            style={'textAlign': 'center', 'padding-left':'10%', 'padding-right':'10%', 'width': '80%'}
        ),
        html.Div(
            children=[
                html.Div(
                    id='graph-div',
                    children=[
                        html.H2(dcc.Markdown("Online data"), style={'textAlign': 'left'}),
                        dcc.Graph(id='avn-graph', animate=True)
                    ],
                    style={'display': 'inline-block', 'align-self': 'left', 'width': '70%'}
                ),
                html.Div(
                    id='table-div',
                    children=[
                        html.H2(dcc.Markdown("Stats"), style={'textAlign': 'left'})
                        
                    ],
                    style={'display': 'inline-block', 'align-self': 'right', 'width': '20%'}
                ),
            ],
            style={'textAlign': 'center', 'padding-left':'10%', 'padding-right':'10%', 'width': '80%'}
        ),
    ],
)


@app.callback(
    Output('avn-db-store', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def store_data(n, data):
    try:
        conn = Dateaubase.connect_local(LOCAL_SERVER, DATABASE_NAME)
    except Exception:
        raise PreventUpdate
    print('Store update has started')
    end = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    start_time = datetime.now(timezone.utc) - timedelta(minutes=MINUTES_OF_DATA)
    try:
        stored_df = pd.read_json(data)
    except Exception:
        stored_df = pd.DataFrame()
    if len(stored_df) == 0:
        start = datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
    else:
        print('what is the latest time?')
        print(pd.to_datetime(list(stored_df.index)[-1]))
        last_time = pd.to_datetime(list(stored_df.index)[-1])
        print(f'the type is {type(last_time)}')

        if last_time < start_time:
            start = datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
        else:
            start = datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
    Project = 'pilEAUte'
    Location = [
        'Primary settling tank effluent',
        'Pilote effluent',
        'Pilote effluent',
        'Pilote reactor 5']
    equip_list = [
        'Ammo_005',
        'Varion_002',
        'Varion_002',
        'FIT-430']
    param_list = [
        'NH4-N',
        'NH4-N',
        'NO3-N',
        'Flowrate (Gas)']
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
    if len(stored_df.count()) == 0:
        print('No stored data')
        complete_df = new_df
    else:
        if length_new == 0:
            print('No new data. Update aborted.')
            raise PreventUpdate
        else:
            print('Updating store with new data')
            # print(f'trying to concat dataframes. New df has {length_new} lines')
            complete_df = pd.concat([stored_df, new_df], sort=True)
            complete_df = complete_df.iloc[length_new:]
    print('Storing data')
    json_data = complete_df.to_json(date_format='iso')
    return json_data


@app.callback(
    Output('avn-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def avn_graph(data):
    pass
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        fig = PlottingTools.threefigs(df)
        print('AvN fig has been drawn')
        return fig
''

'''@app.callback(
    Output('avn-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def avn_graph(data):
    pass
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        fig = PlottingTools.avn_plot(df)
        print('AvN fig has been drawn')
        return fig


@app.callback(
    Output('fraction-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def fraction_graph(data):
    pass
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        fig = PlottingTools.airflow_plot(df)
        print('Airflow fig has been drawn')
        return fig


@app.callback(
    Output('airflow-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def airflow_graph(data):
    pass
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        fig = PlottingTools.airflow_plot(df)
        print('Airflow fig has been drawn')
        return fig'''

if __name__ == '__main__':
    app.run_server(debug=True)
