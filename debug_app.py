from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import ptvsd

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import plotly.io as pio

import Dateaubase
import PlottingTools
import calculateKPIs


pio.templates.default = "plotly_white"

pd.options.display.float_format = '{:,.2f}'.format


engine = Dateaubase.create_connection()

print('connect successful')
# USER DEFINED PARAMETERS
NEW_DATA_INTERVAL = 60  # seconds
DAYS_OF_DATA = 0.1  # days
OFFSET = 0  # weeks

# INITIALIZATION
INTERVAL_LENGTH_SEC = DAYS_OF_DATA * 24 * 60 * 60
STORE_MAX_LENGTH = INTERVAL_LENGTH_SEC  # worst-case of sensor that updates every second
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# EXTRACT DESIRED DATA
def AvN_shopping_list(beginning_string, ending_string):
    Project = 'pilEAUte'
    Location = [
        'Pilote influent',
        'Copilote influent',
        'Primary settling tank effluent',
        'Primary settling tank effluent',
        'Primary settling tank effluent',
        'Pilote effluent',
        'Pilote effluent',
        'Pilote effluent',
        'Pilote reactor 5']
    equip_list = [
        'FIT-110',
        'FIT-120',
        'Ammo_005',
        'Spectro_010',
        'Spectro_010',
        'Varion_002',
        'Varion_002',
        'Varion_002',
        'FIT-430']
    param_list = [
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'NH4-N',
        'COD',
        'NO3-N',
        'NH4-N',
        'NO3-N',
        'Temperature',
        'Flowrate (Gas)']
    shopping_list = {}
    for i in range(len(param_list)):
        shopping_list[i] = {
            'Start': Dateaubase.date_to_epoch(beginning_string),
            'End': Dateaubase.date_to_epoch(ending_string),
            'Project': Project,
            'Location': Location[i],
            'Parameter': param_list[i],
            'Equipment': equip_list[i]
        }
    return shopping_list


app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        dcc.Interval(id='refresh-interval', interval=NEW_DATA_INTERVAL * 1000, n_intervals=0),
        html.H1(id='msg'),
        dcc.Graph(id='graph'),
    ]
)


@app.callback(
    Output('msg', 'children'),
    [Input('refresh-interval', 'n_intervals')])
def store_data(n):
    end_time, start_time = (
        pd.to_datetime(
            datetime.utcnow() - timedelta(weeks=OFFSET)
        ).tz_localize("UTC"),
        pd.to_datetime(
            datetime.utcnow() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
        ).tz_localize("UTC"))

    end_string = datetime.strftime(end_time, TIME_FORMAT)
    start_string = datetime.strftime(start_time, TIME_FORMAT)

    extract_list = AvN_shopping_list(start_string, end_string)
    print('trying to get new data')
    new_df = Dateaubase.extract_data(engine, extract_list)
    return('data extracted')


@app.callback(
    Output('graph', 'figure'),
    [Input('refresh-interval', 'n_intervals')])
def simple_graph(n):
    end_time, start_time = (
        pd.to_datetime(
            datetime.utcnow() - timedelta(weeks=OFFSET)
        ).tz_localize("UTC"),
        pd.to_datetime(
            datetime.utcnow() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
        ).tz_localize("UTC"))

    end_string = datetime.strftime(end_time, TIME_FORMAT)
    start_string = datetime.strftime(start_time, TIME_FORMAT)

    extract_list = AvN_shopping_list(start_string, end_string)
    print('trying to get new data')
    new_df = Dateaubase.extract_data(engine, extract_list)
    fig = PlottingTools.debug_app(new_df)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
else:
    ptvsd.enable_attach(log_dir='C:\\Users\\Administrator\\Desktop\\pileaute_dash_logs')
    server = app.server