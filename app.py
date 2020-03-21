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
import calculateKPIs

pio.templates.default = "plotly_white"

pd.options.display.float_format = '{:,.2f}'.format


engine = Dateaubase.create_connection()

print('connect successful')
# USER DEFINED PARAMETERS
NEW_DATA_INTERVAL = 10  # seconds
DAYS_OF_DATA = 1  # days
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
        dcc.Store(id='avn-db-store'),
        html.Div(
            children=[
                html.Img(
                    src='assets/flowsheetPilEAUte_avn.png',
                    style={'align': 'middle'}
                ),
            ],
            style={
                'textAlign': 'center',
                'paddingLeft': '0%',
                'paddingRight': '0%',
                'width': '100%',
                # 'borderStyle': 'solid',
            }
        ),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    id='graph-div',
                    children=[
                        # html.H2(dcc.Markdown("Online data"), style={'textAlign': 'center'}),
                        dcc.Graph(id='avn-graph')
                    ],
                    style={
                        'float': 'left',
                        'width': '70%',
                        # 'borderStyle': 'solid',
                        'display': 'inline-block',
                        'paddingLeft': '2%',
                        'paddingRight': '0%',
                    }
                ),
                html.Div(
                    id='table-div',
                    children=[
                        # html.H2(dcc.Markdown("Aggregate statistics"), style={'textAlign': 'center'}),
                        html.Div(
                            id='floor-1',
                            children=[
                                html.Div(
                                    children=[
                                        html.H4(
                                            'Influent',
                                            style={'textAlign': 'left'}
                                        ),
                                        dash_table.DataTable(
                                            id='influent-table',
                                            columns=[{"name": i, "id": i} for i in ['Parameter', 'Now', 'Last 24 hrs']],
                                            style_as_list_view=True,
                                            style_header={
                                                'fontWeight': 'bold',
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                            },
                                            style_cell_conditional=[
                                                {
                                                    'if': {'column_id': c},
                                                    'textAlign': 'left'
                                                } for c in ['Parameter']
                                            ],
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(248, 248, 248)'
                                                }
                                            ],
                                        ),
                                    ],
                                    style={
                                        'display': 'inline-block',
                                        'alignSelf': 'left',
                                        'width': '96%',
                                        'paddingLeft': '2%',
                                        'paddingRight': '2%'
                                    },
                                ),
                                html.Br(),
                                html.Div(
                                    children=[
                                        html.H4(
                                            'Effluent',
                                            style={'textAlign': 'left'},
                                        ),
                                        dash_table.DataTable(
                                            id='effluent-table',
                                            columns=[{"name": i, "id": i} for i in ['Parameter', 'Now', 'Last 24 hrs']],
                                            style_as_list_view=True,
                                            style_header={
                                                'fontWeight': 'bold',
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                            },
                                            style_cell_conditional=[
                                                {
                                                    'if': {'column_id': c},
                                                    'textAlign': 'left'
                                                } for c in ['Parameter']
                                            ],
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(248, 248, 248)'
                                                }
                                            ],
                                        ),
                                    ],
                                    style={
                                        'display': 'inline-block',
                                        'alignSelf': 'left',
                                        'width': '96%',
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
                                    children=[
                                        html.H4(
                                            'Cumulative Stats',
                                            style={'textAlign': 'left'}
                                        ),
                                        dash_table.DataTable(
                                            id='bioreactor-table',
                                            columns=[{"name": i, "id": i} for i in ['Parameter', 'Last 24 hrs']],
                                            style_as_list_view=True,
                                            style_header={
                                                'fontWeight': 'bold',
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                            },
                                            style_cell_conditional=[
                                                {
                                                    'if': {'column_id': c},
                                                    'textAlign': 'left'
                                                } for c in ['Parameter']
                                            ],
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(248, 248, 248)'
                                                }
                                            ],
                                        )
                                    ],
                                    style={
                                        'display': 'inline-block',
                                        'alignSelf': 'right',
                                        'width': '96%',
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
                        # 'borderStyle': "solid",
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
        end_time, start_time = (
            pd.to_datetime(
                datetime.utcnow() - timedelta(weeks=OFFSET)
            ).tz_localize("UTC"),
            pd.to_datetime(
                datetime.utcnow() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
            ).tz_localize("UTC"))
    except TypeError:
        end_time, start_time = (
            pd.to_datetime(
                datetime.utcnow() - timedelta(weeks=OFFSET)
            ).tz_localize("UTC"),
            pd.to_datetime(
                datetime.utcnow() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
            ).tz_localize("UTC"))

    end_string = datetime.strftime(end_time, TIME_FORMAT)
    start_string = datetime.strftime(start_time, TIME_FORMAT)

    try:
        stored_df = pd.read_json(data)
    except Exception:
        stored_df = pd.DataFrame()
    if len(stored_df) != 0:
        last_time = pd.to_datetime(list(stored_df.index)[-1])
        last_string = last_time.strftime(TIME_FORMAT)
        # print(start_string)
        # print(f'{last_string} - last update')
        if last_time > start_time:
            start_string = last_string
    # print(f'{len(stored_df)} points are in the store')
    # print(f'Data from {start_string} to {end_string} will be extracted.')
    extract_list = AvN_shopping_list(start_string, end_string)
    new_df = Dateaubase.extract_data(engine, extract_list)

    if len(stored_df) == 0:
        # print('No stored data')
        complete_df = new_df
    else:
        if len(new_df) == 0:
            # print('No new data. Update aborted.')
            raise PreventUpdate
        else:
            current_time = pd.to_datetime(datetime.now())
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
        Qair_col = df["pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)"]
        _, peak_average = calculateKPIs.peak_stats(Qair_col, 400 / (60 * 1000))
        df = pd.concat([df, peak_average], axis=1, sort=False)
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
        COD_col = data['pilEAUte-Primary settling tank effluent-Spectro_010-COD'] * 1000
        # print(NH4_col.tail())
        NH4_now, NH4_24 = calculateKPIs.stats_24(NH4_col)

        COD_now, COD_24 = calculateKPIs.stats_24(COD_col)

        ratio_now = COD_now / NH4_now
        ratio_24 = COD_24 / NH4_24
        df = pd.DataFrame.from_dict({
            'Parameter': ['COD (mg/l)', 'NH4 (mg/l)', 'COD/NH4 (-)'],
            'Now': [f'{COD_now:.2f}', f'{NH4_now:.2f}', f'{ratio_now:.2f}'],
            'Last 24 hrs': [f'{COD_24:.2f}', f'{NH4_24:.2f}', f'{ratio_24:.2f}'],
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

        # effluent stats
        NH4_col = data['pilEAUte-Pilote effluent-Varion_002-NH4_N'] * 1000
        NO3_col = data['pilEAUte-Pilote effluent-Varion_002-NO3_N'] * 1000
        NH4in_col = data['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N']
        NO3in_col = data['pilEAUte-Primary settling tank effluent-Spectro_010-NO3_N']
        NH4_now, NH4_24 = calculateKPIs.stats_24(NH4_col)

        NO3_now, NO3_24 = calculateKPIs.stats_24(NO3_col)

        NO2_now, NO2_24 = 0, 0

        AvN_now = NH4_now - (NO3_now + NO2_now)
        AvN_24 = NH4_24 - (NO3_24 + NO2_24)

        # influent values
        NH4in_now, NH4in_24 = calculateKPIs.stats_24(NH4in_col)
        NO3in_now, NO3in_24 = calculateKPIs.stats_24(NO3in_col)

        df = pd.DataFrame.from_dict({
            'Parameter': ['NH4 (mg/l)', 'NO2 (mg/l)', 'NO3 (mg/l)', 'AvN difference (mg/l)'],
            'Now': [f'{NH4_now:.2f}', f'{NO2_now:.2f}', f'{NO3_now:.2f}', f'{AvN_now:.2f}'],
            'Last 24 hrs': [f'{NH4_24:.2f}', f'{NO2_24:.2f}', f'{NO3_24:.2f}', f'{AvN_24:.2f}'],
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
        air_col = data['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)']  # m3/s
        pilwater_col = data['pilEAUte-Pilote influent-FIT_110-Flowrate (Liquid)']  # m3/s
        NH4eff_col = data['pilEAUte-Pilote effluent-Varion_002-NH4_N'] / 1000  # mg/l to kg/m3
        NO3eff_col = data['pilEAUte-Pilote effluent-Varion_002-NO3_N']  # kg/m3

        NH4in_col = data['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N'] / 1000  # mg/l to kg/m3
        NO3in_col = data['pilEAUte-Primary settling tank effluent-Spectro_010-NO3_N']  # kg/m3

        totNH4in = calculateKPIs.integrate_flow(NH4in_col)
        totNO3in = calculateKPIs.integrate_flow(NO3in_col)
        totNO2eff = 0
        totNH4eff = calculateKPIs.integrate_flow(NH4eff_col)
        totNO3eff = calculateKPIs.integrate_flow(NO3eff_col)
        tot_tin = (totNH4in + totNO3in) - (totNH4eff + totNO3eff + totNO2eff)
        tot_air = calculateKPIs.integrate_flow(air_col)
        tot_water = calculateKPIs.integrate_flow(pilwater_col)
        # print(f'Total air,(m3) {tot_air}')
        # print(f'Total water, (m3), {tot_water}')
        # print(f'Total TIN removed, kg, {tot_tin / 1000}')

        tin_air = tot_tin / tot_air
        air_water = tot_air / tot_water

        df = pd.DataFrame.from_dict({
            'Parameter': [
                'Volume of water treated (m3/d)',
                'Volume of air (m3/d)',
                'TIN removed (g/d)',
                'Volume of air / Volume of treated water (m3/m3)',
                'TIN removed/m3 air (g N/m3)',
            ],
            'Last 24 hrs': [
                f'{tot_water:.1f}',
                f'{tot_air:.1f}',
                f'{tot_tin:.1f}',
                f'{air_water:.1f}',
                f'{tin_air:.3f}',
            ],
        })
        return df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
