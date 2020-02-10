from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.io as pio

import Dateaubase
import PlottingTools
import kpi

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
pio.templates.default = "plotly_white"

pd.options.display.float_format = '{:,.2f}'.format
# USER DEFINED PARAMETERS
NEW_DATA_INTERVAL = 10  # seconds
DAYS_OF_DATA = 1 / 24  # days
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
        'Pilote effluent',
        'Pilote effluent',
        'Pilote effluent',
        'Pilote reactor 5']
    equip_list = [
        'FIT-110',
        'FIT-120',
        'Ammo_005',
        'Varion_002',
        'Varion_002',
        'Varion_002',
        'FIT-430']
    param_list = [
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'NH4-N',
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
            style={
                'textAlign': 'center',
                'paddingLeft': '0%',
                'paddingRight': '0%',
                'width': '100%',
                'borderStyle': 'solid',
            }
        ),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    id='graph-div',
                    children=[
                        html.H2(dcc.Markdown("Online data"), style={'textAlign': 'center'}),
                        dcc.Graph(id='avn-graph')
                    ],
                    style={
                        'float': 'left',
                        'width': '70%',
                        'borderStyle': 'solid',
                        'display': 'inline-block',
                        'paddingLeft': '2%',
                        'paddingRight': '0%',
                    }
                ),
                html.Div(
                    id='table-div',
                    children=[
                        html.H2(dcc.Markdown("Stats"), style={'textAlign': 'center'}),
                        html.Div(
                            id='floor-1',
                            children=[
                                html.Div(
                                    children=[
                                        html.H4('Influent'),
                                        dash_table.DataTable(
                                            id='influent-table',
                                            columns=[{"name": i, "id": i} for i in ['Parameter', 'Value (mg/l)']],
                                        ),
                                    ],
                                    style={
                                        'display': 'inline-block',
                                        'alignSelf': 'left',
                                        'width': '40%',
                                        'paddingLeft': '2%',
                                        'paddingRight': '2%'
                                    },
                                ),
                                html.Div(
                                    children=[
                                        html.H4('Effluent'),
                                        dash_table.DataTable(
                                            id='effluent-table',
                                            columns=[{"name": i, "id": i} for i in ['Parameter', 'Value (mg/l)']],
                                        ),
                                    ],
                                    style={
                                        'display': 'inline-block',
                                        'alignSelf': 'right',
                                        'width': '40%',
                                        'paddingLeft': '2%',
                                        'paddingRight': '2%',
                                    },
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Div(
                            id='floor-2',
                            children=[
                                html.Div(
                                    children=dash_table.DataTable(
                                        id='bioreactor-table',
                                        columns=[{"name": i, "id": i} for i in ['Qair, AE (m3/h)', 'Temperaure (°C)']],
                                    ),
                                    style={
                                        'display': 'inline-block',
                                        'alignSelf': 'left',
                                        'width': '40%',
                                        'paddingLeft': '2%',
                                        'paddingRight': '2%'
                                    },
                                ),
                            ],
                        ),
                    ],
                    style={
                        'float': 'right',
                        'width': '25%',
                        'borderStyle': "solid",
                        'display': 'inline-block',
                        'paddingLeft': '0%',
                        'paddingRight': '0%',
                    }
                ),
            ],
            style={'textAlign': 'center', 'paddingLeft': '0%', 'paddingRight': '0%', 'width': '100%'}
        ),
    ],
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
    # print('Store update has started')
    try:
        end_time, start_time = (
            pd.to_datetime(
                datetime.now() - timedelta(weeks=OFFSET)
            ).tz_localize('EST'),
            pd.to_datetime(
                datetime.now() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
            ).tz_localize('EST'))
    except TypeError:
        end_time, start_time = (
            pd.to_datetime(
                datetime.now() - timedelta(weeks=OFFSET)
            ).tz_convert('EST'),
            pd.to_datetime(
                datetime.now() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
            ).tz_convert('EST'))

    end_string = datetime.strftime(end_time, TIME_FORMAT)
    start_string = datetime.strftime(start_time, TIME_FORMAT)

    try:
        stored_df = pd.read_json(data)
    except Exception:
        stored_df = pd.DataFrame()
    if len(stored_df) != 0:
        last_time = pd.to_datetime(list(stored_df.index)[-1])
        if last_time.tz is None:
            last_time = last_time.tz_localize('EST')
        else:
            last_time = last_time.tz_convert('EST')
        last_string = last_time.strftime(TIME_FORMAT)
        # print(start_string)
        # print(f'{last_string} - last update')
        if last_time > start_time:
            start_string = last_string
    # print(f'{len(stored_df)} points are in the store')
    # print(f'Data from {start_string} to {end_string} will be extracted.')
    extract_list = AvN_shopping_list(start_string, end_string)
    new_df = Dateaubase.extract_data(conn, extract_list)

    if len(stored_df) == 0:
        # print('No stored data')
        complete_df = new_df
    else:
        if len(new_df) == 0:
            # print('No new data. Update aborted.')
            raise PreventUpdate
        else:
            current_time = pd.to_datetime(datetime.now())
            if current_time.tz is None:
                current_time = current_time.tz_localize('EST')
            else:
                current_time = current_time.tz_convert('EST')
            print(current_time)
            print('Updating store with new data')
            print(f'{len(new_df)} new lines')
            # print(f'stored_df has {len(stored_df)} lines')
            complete_df = pd.concat([stored_df, new_df], sort=True)
            complete_df = complete_df.iloc[len(new_df):]
            # print(f'complete_df has {len(complete_df)} lines')
    # print('Storing data')
    json_data = complete_df.to_json(date_format='iso')
    return json_data


@app.callback(
    Output('avn-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def avn_graph(data):
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        fig = PlottingTools.threefigs(df)
        # print('AvN fig has been created')
        return fig


@app.callback(
    Output('influent-table', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def update_influent_stats(refresh, data):
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        NH4_col = data['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N']
        NH4_min, NH4_max, NH4_avg, _ = kpi.stats(NH4_col)
        df = pd.DataFrame.from_dict({
            'Parameter': ['NH4_min', 'NH4_avg', 'NH4_max'],
            'Value (mg/l)': [f'{NH4_min:.2f}', f'{NH4_avg:.2f}', f'{NH4_max:.2f}']
        })
        return df.to_dict('records')


@app.callback(
    Output('effluent-table', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def update_effluent_stats(refresh, data):
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        NH4_col = data['pilEAUte-Pilote effluent-Varion_002-NH4_N'] * 1000
        NO3_col = data['pilEAUte-Pilote effluent-Varion_002-NO3_N'] * 1000
        _, _, NH4_avg, _ = kpi.stats(NH4_col)
        _, _, NO3_avg, _ = kpi.stats(NO3_col)
        avn_ratio = NH4_avg / NO3_avg
        df = pd.DataFrame.from_dict({
            'Parameter': ['NH4_eff, avg', 'NO3_eff, avg', 'AvN ratio'],
            'Value (mg/l)': [f'{NH4_avg:.2f}', f'{NO3_avg:.2f}', f'{avn_ratio:.2f}']
        })
        return df.to_dict('records')


@app.callback(
    Output('bioreactor-table', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def update_biological_stats(refresh, data):
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        air_col = data['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)']
        temp_col = data['pilEAUte-Pilote effluent-Varion_002-Temperature']
        _, _, air_avg, _ = kpi.stats(air_col, rate=True)
        air_avg *= 3600
        _, _, temp_avg, _ = kpi.stats(temp_col)
        df = pd.DataFrame.from_dict({
            'Qair, AE (m3/h)': [f'{air_avg:.2f}'],
            'Temperaure (°C)': [f'{temp_avg:.2f}']
        })
        return df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
