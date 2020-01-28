from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.io as pio

import dateaubase
import plottingtools

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
pio.templates.default = "plotly_white"

DEBUG_START = "2017-08-01 00:00:00"
NEW_DATA_INTERVAL = 30  # in seconds
DAYS_OF_DATA = 1
INTERVAL_LENGTH_SEC = DAYS_OF_DATA * 24 * 60 * 60
STORE_MAX_LENGTH = INTERVAL_LENGTH_SEC  # worst-case of sensor that updates every second
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def AvN_shopping_list(beginning_string, ending_string):
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
    shopping_list = {}
    for i in range(len(param_list)):
        shopping_list[i] = {
            'Start': dateaubase.date_to_epoch(beginning_string),
            'End': dateaubase.date_to_epoch(ending_string),
            'Project': Project,
            'Location': Location[i],
            'Parameter': param_list[i],
            'Equipment': equip_list[i]
        }
    return shopping_list


def build_param_table(_id):
    table = dash_table.DataTable(
        id=_id,
        columns=[
            {'name': 'Parameter', 'id': 'Parameter', 'editable': False},
            {'name': 'Value', 'id': 'Value', 'editable': True},
        ],
        style_table={
            'width': '100%',
            'maxHeight': '300',
            'overflowY': 'scroll'
        },
        style_data={'whiteSpace': 'normal'},
        # content_style='grow',
        css=[
            {'selector': 'td.cell--selected *, td.focused *', 'rule': 'text-align: center;'},
            {'selector': '.dash-cell div.dash-cell-value',
                'rule': '''font-family: "Helvetica Neue";
                    display: inline;
                    white-space: inherit;
                    overflow: inherit;
                    text-overflow: inherit;
                    font-size: 10px;'''},
        ],
        style_cell_conditional=[
            {'if': {'column_id': 'Parameter'},
                'minWidth': '50%', 'maxWidth': '50%', 'textAlign': 'left'},
            {'if': {'column_id': 'Value'},
                'minWidth': '50%', 'maxWidth': '50%', 'textAlign': 'center'},
        ],
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'fontFamily': 'Helvetica Neue',
            'fontSize': '12px',
        },
        editable=True,
        style_as_list_view=True,
    )
    return table


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
            style={'textAlign': 'center', 'padding-left': '10%', 'padding-right': '10%', 'width': '80%'}
        ),
        html.Div(
            children=[
                html.Div(
                    id='graph-div',
                    children=[
                        html.H2(dcc.Markdown("Online data"), style={'textAlign': 'left'}),
                        dcc.Graph(id='avn-graph')
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
            style={'textAlign': 'center', 'padding-left': '10%', 'padding-right': '10%', 'width': '80%'}
        ),
    ],
)


@app.callback(
    Output('avn-db-store', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def store_data(n, data):
    try:
        _, conn = dateaubase.create_connection()
    except Exception:
        raise PreventUpdate
    print('Store update has started')
    end_time = pd.to_datetime(
        datetime.now() - timedelta(weeks=38)
    ).tz_localize('EST')
    start_time = pd.to_datetime(
        datetime.now() - timedelta(weeks=38) - timedelta(seconds=INTERVAL_LENGTH_SEC)
    ).tz_localize('EST')

    end_string = datetime.strftime(end_time, TIME_FORMAT)
    start_string = datetime.strftime(start_time, TIME_FORMAT)

    try:
        stored_df = pd.read_json(data)
    except Exception:
        stored_df = pd.DataFrame()
    if len(stored_df) != 0:
        last_time = pd.to_datetime(list(stored_df.index)[-1]).tz_convert('EST')
        last_string = last_time.strftime(TIME_FORMAT)
        print(start_string)
        print(last_string)
        if last_time > start_time:
            start_string = last_string
    print(f'{len(stored_df)} points are in the store')
    print(f'Data from {start_string} to {end_string} will be extracted.')
    extract_list = AvN_shopping_list(start_string, end_string)
    new_df = dateaubase.extract_data(conn, extract_list)

    if len(stored_df) == 0:
        print('No stored data')
        complete_df = new_df
    else:
        if len(new_df) == 0:
            print('No new data. Update aborted.')
            raise PreventUpdate
        else:
            print('Updating store with new data')
            print(f'trying to concat dataframes. New df has {len(new_df)} lines')
            complete_df = pd.concat([stored_df, new_df], sort=True)
            complete_df = complete_df.iloc[len(new_df):]
    print(f'{len(complete_df)} are stored')
    print('Storing data')
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
        fig = plottingtools.threefigs(df)
        print('AvN fig has been created')
        return fig


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
        fig = plottingtools.avn_plot(df)
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
        fig = plottingtools.airflow_plot(df)
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
        fig = plottingtools.airflow_plot(df)
        print('Airflow fig has been drawn')
        return fig'''

if __name__ == '__main__':
    app.run_server(debug=True)
