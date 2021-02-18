from datetime import datetime, timedelta
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from collections import namedtuple
from sqlalchemy import create_engine
from urllib import parse
import time

import plotly.io as pio

import Dateaubase
import PlottingTools
import calculateKPIs

import importlib
importlib.reload(PlottingTools)

# # Setting constants
# database_name = 'dateaubase2020'
# remote_server = r'132.203.190.77'

# with open('login.txt') as f:
# 	username = f.readline().strip()
# 	password = f.readline().strip()


# def connect_remote(server, database, login_file):
# 	with open(login_file) as f:
# 		username = f.readline().strip()
# 		password = parse.quote_plus(f.readline().strip())
# 	engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server', connect_args={'connect_timeout': 2}, fast_executemany=True)
# 	return engine


# engine = connect_remote(remote_server, database_name, 'login.txt')


# if Dateaubase.engine_runs(engine):
#     print('connect successful')



# # Default plotting theme
# pio.templates.default = "plotly_white"
# # external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_scripts = ['https://cdn.jsdelivr.net/npm/file-saver@2.0.2/dist/FileSaver.min.js']
# app = dash.Dash(__name__, external_scripts=external_scripts,)
# app.config['suppress_callback_exceptions'] = True

try:
    COMPUTER_NAME = os.environ['COMPUTERNAME']
except KeyError:
    COMPUTER_NAME = 'not_windows'

DATABASE_NAME = 'dateaubase2020'

if COMPUTER_NAME == 'GCI-PR-DATEAU02':
    print('connecting to local DB')
    conn = Dateaubase.connect_local(Dateaubase.local_server, DATABASE_NAME)
else:
    print('connecting to remote DB')
    conn = Dateaubase.connect_remote(Dateaubase.remote_server, DATABASE_NAME, 'login.txt')




pio.templates.default = "plotly_white"

pd.options.display.float_format = '{:,.2f}'.format






from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from collections import namedtuple
from sqlalchemy import create_engine
from urllib import parse
import time
from datetime import datetime
from datetime import timedelta


import plotly.io as pio

import Dateaubase
import PlottingTools
import calculateKPIs
# USER DEFINED PARAMETERS
# USER DEFINED PARAMETERS
NEW_DATA_INTERVAL = 300  # seconds
DAYS_OF_DATA = 1  # days
OFFSET = 52  # weeks

# INITIALIZATION
INTERVAL_LENGTH_SEC = DAYS_OF_DATA * 24 * 60 * 60
STORE_MAX_LENGTH = INTERVAL_LENGTH_SEC  # worst-case of sensor that updates every second
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'



# EXTRACT DESIRED DATA
def AvN_shopping_list(beginning_string, ending_string):
    Project = 'pilEAUte'
    Location = [
        'Primary settling tank influent',
        'Pilote influent',
        'Copilote influent',
        'Primary settling tank effluent',
        'Primary settling tank effluent',
        'Primary settling tank effluent',
        'Primary settling tank effluent', # ammo
        'Primary settling tank effluent',
        'Primary settling tank effluent',
        'Primary settling tank effluent',
        'Primary settling tank effluent',# spectro
        'Pilote effluent','Pilote effluent',
        'copilote effluent','copilote effluent', # Varion
        'Pilote reactor 5',
        'copilote reactor 5',
        'Pilote reactor 4', 'copilote reactor 4',
        'Pilote reactor 5', 'copilote reactor 5',
        'Pilote sludge recycle','Copilote sludge recycle',
        'Pilote effluent', 'copilote effluent']
    equip_list = [
        'FIT-100',
        'FIT-110',
        'FIT-120', # flow
        'Ammo_005',
        'Ammo_005',
        'Ammo_005',
        'Ammo_005',# ammo
        'Spectro_010',
        'Spectro_010',
        'Spectro_010',
        'Spectro_010', # spectro
        'Varion_002','Varion_002',
        'Varion_001','Varion_001', # Varion
        'FIT-430', 
        'FIT-460',
        'AIT-241', 'AIT-341',
        'AIT-250', 'AIT-350',
        'AIT-260','AIT-360',
        'TurbR200','TurbR300' ]
    param_list = [
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'NH4-N',
        'K',
        'Temperature',
        'pH',
        'TSS',
        'COD',
        'CODf',
        'NO3-N',
        'NH4-N','NO3-N',
        'NH4-N','NO3-N',
        'Flowrate (Gas)',
        'Flowrate (Gas)',
        'DO','DO',
        'TSS','TSS',
        'TSS','TSS',
        'Turbidity','Turbidity' ]
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



# EXTRACT DESIRED DATA
def Energy_shopping_list(beginning_string, ending_string):
    Project = 'pilEAUte'
    Location = [
        'Primary settling tank influent',
        'Pilote influent',
        'Copilote influent',
        'Pilote sludge recycle',
        'Copilote sludge recycle',
        'Pilote internal recycle IN',
        'Copilote internal recycle IN',
        'Pilote reactor 3','Pilote reactor 4','Pilote reactor 5',
        'Copilote reactor 3','Copilote reactor 4','Copilote reactor 5']
    equip_list = [
        'FIT-100',
        'FIT-110',
        'FIT-120',# flow
        'FIT-260',
        'FIT-360',
        'FIT-250',
        'FIT-350',
        'FIT-410','FIT-420','FIT-430',
        'FIT-440','FIT-450','FIT-460'
         ]
    param_list = [
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Gas)','Flowrate (Gas)','Flowrate (Gas)',
        'Flowrate (Gas)','Flowrate (Gas)','Flowrate (Gas)']
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
         dcc.Store(id='energydata'),
        html.Div(
            children=[
                html.Img(
                    src='assets/flowsheetPilEAUte1.png',
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

    html.Div([
        html.Div([
            html.Div([
            html.H2('Influent load [g/d]', style={'textAlign': 'center', 'color':'royalblue'}),
            dcc.Graph(id='InfluentLoad')], className="four columns"),

            html.Div([
            html.H2('Influent concentration [mg/L]', style={'textAlign': 'center', 'color':'royalblue'}),
            dcc.Graph(id='InfluentConcentration')], className="five columns"),

            html.Div(children= [
            #html.H2(dcc.Markdown('Influent Parameter'), style={'textAlign': 'center', 'color':'royalblue'}),
            html.Div(dcc.Graph(id='HRT_SRT'))
            ], className="three columns"),])
            ]),

        html.Br(),
        html.Div(
            children=[
                html.Div(
                    id='graph-div',
                    children=[
                        # html.H2(dcc.Markdown("Online data"), style={'textAlign': 'center'}),
                        #dcc.Graph(id='avn-graph',className='three columns'),
                        html.Div([
                            html.H2(dcc.Markdown('oxygen level'), style={'textAlign': 'center', 'color':'royalblue'}), dcc.Graph(id='oxylevel')], className="six columns"),
                        html.Div([
                            html.H2(dcc.Markdown('TSS concentration'), style={'textAlign': 'center', 'color':'royalblue'}),
                            dcc.Graph(id='TSSconcen')], className="six columns"),
                    ],
                    style={
                        'float': 'left',
                        'width': '100%',
                        # 'borderStyle': 'solid',
                        'display': 'inline-block',
                        'paddingLeft': '2%',
                        'paddingRight': '0%',
                    }
                ),
            ],
            style={'textAlign': 'center', 'paddingLeft': '0%', 'paddingRight': '0%', 'width': '100%'}
        ),

     html.Div(children=[html.H2(dcc.Markdown('Effluent'),style={'textAlign': 'center', 'color': 'royalblue'}),
        dcc.Graph(id='Effluent_concen')], 
         className="seven columns"),
    html.Div(children=[html.H2(dcc.Markdown('Energy statement (kWh·d-1)'),style={'textAlign': 'center', 'color': 'royalblue'}),
        dcc.Graph(id='Energy_bilan')], 
         className="four columns"),
])



#%%

@app.callback(
    Output('avn-db-store', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def store_data(n, data):
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

    print(f'{len(stored_df)} points are in the store')
    print(f'Data from {start_string} to {end_string} will be extracted.')
    extract_list = AvN_shopping_list(start_string, end_string)
    print('trying to get new data')

    new_df = Dateaubase.extract_data(engine, extract_list)
 # add rain value to dataextracted.
    Rainquery = 'SELECT [Timestamp],  [Value] FROM [dateaubase2020].[dbo].[value] WHERE Metadata_ID = 101 AND Timestamp> ='+str(Dateaubase.date_to_epoch(start_string))+ 'AND Timestamp <= ' +str(Dateaubase.date_to_epoch(end_string))  
    Rain=pd.read_sql(Rainquery, engine).drop_duplicates(subset=['Timestamp'],keep='first')
    Rain.rename(columns={'Timestamp':'datetime','Value':'Rain'},inplace=True)    
    Rain['datetime']= [datetime.fromtimestamp(d).strftime('%Y-%m-%d %H-%M-%S') for d in Rain['datetime']]
    Rain['datetime']=pd.to_datetime(Rain['datetime'],format='%Y-%m-%d %H-%M-%S')
    Rain=Rain.set_index('datetime')
    new_df=pd.concat([new_df, Rain], axis=1)

    print("new_df_TzInfo", new_df.index[0].tzinfo)
    print('data extracted')

    if len(stored_df) == 0:
        print('No stored data')
        complete_df = new_df
    else:
        if len(new_df) == 0:
            print('No new data. Update aborted.')
            raise PreventUpdate
        else:
            current_time = pd.to_datetime(datetime.now())
            #print(current_time)
            print('Updating store with new data')
            print(f'{len(new_df)} new lines')
            print(f'stored_df has {len(stored_df)} lines')
            complete_df = pd.concat([stored_df, new_df], sort=True)
            complete_df = complete_df.iloc[len(new_df):]
            # print(f'complete_df has {len(complete_df)} lines')
    # print('Storing data')
    json_data = complete_df.to_json(date_format='iso')
    return json_data



@app.callback(
    Output('influent-table', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def update_influent_stats(refresh, data):
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:
            data.index = data.index.map(lambda x: x.tz_localize(None))
            NH4_col = data['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N']
            COD_col = data['pilEAUte-Primary settling tank effluent-Spectro_010-COD'] * 1000
            print(NH4_col.mean())
            NH4_now, NH4_24 = calculateKPIs.stats_24(NH4_col, OFFSET)

            COD_now, COD_24 = calculateKPIs.stats_24(COD_col, OFFSET)

            ratio_now = COD_now / NH4_now
            ratio_24 = COD_24 / NH4_24
            df = pd.DataFrame.from_dict({
                'Parameter': ['COD (mg/l)', 'NH4 (mg/l)', 'COD/NH4 (-)'],
                'Now': [f'{COD_now:.2f}', f'{NH4_now:.2f}', f'{ratio_now:.2f}'],
                'Last 24 hrs': [f'{COD_24:.2f}', f'{NH4_24:.2f}', f'{ratio_24:.2f}'],
            })
        return df.to_dict('records')



@app.callback(
    Output('InfluentLoad', 'figure'),
    [Input('avn-db-store', 'n_intervals')],
    [State('avn-db-store', 'data')])
def update_Influentload_stats(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.violinplotInfluent(data, OFFSET)
            print('influent load done')
            print('working')
    return fig


@app.callback(
    Output('InfluentConcentration', 'figure'),
    [Input('avn-db-store', 'data')],
    [State('avn-db-store', 'data')])
def update_Influentconcen_stats(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.InfluentConcen(data, OFFSET)

    return fig



@app.callback(
    Output('oxylevel', 'figure'),
    [Input('avn-db-store', 'data')],
    [State('avn-db-store', 'data')])
def update_oxylevel(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.oxylevelplot(data, OFFSET)
    return fig



@app.callback(
    Output('TSSconcen', 'figure'),
    [Input('avn-db-store', 'data')],
    [State('avn-db-store', 'data')])
def update_TSSconcen(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.TSSconcenplot(data, OFFSET)

    return fig


@app.callback(
    Output('Effluent_concen', 'figure'),
    [Input('avn-db-store', 'data')],
    [State('avn-db-store', 'data')])
def update_Effluent_concentrationplot(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.Effluent_concenplot(data, OFFSET)

    return fig


@app.callback(
    Output('HRT_SRT', 'figure'),
    [Input('avn-db-store', 'data')],
    [State('avn-db-store', 'data')])
def update_HRTSRT(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.update_HRT_SRTtable(data, OFFSET)

    return fig



@app.callback(
    Output('energydata','data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('energydata', 'data')])
def store_dataenergy(n, data):
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

    print(f'{len(stored_df)} points are in the store')
    print(f'Data from {start_string} to {end_string} will be extracted for energydata.')
    extract_listEnergy = Energy_shopping_list(start_string, end_string)
    print('trying to get new data')
    energyDataorg = Dateaubase.extract_data(engine, extract_listEnergy)
    energyDataorg .fillna(inplace=True, method='ffill')
    energyData =  energyDataorg.groupby(pd.Grouper(freq='600s')).mean()
    energyData.fillna(inplace=True, method='ffill')
    
    if len(stored_df) == 0:
        print('No stored data')
        complete_df = energyData
    else:
        if len(energyData) == 0:
            print('No new data. Update energy data aborted.')
            raise PreventUpdate
        else:
            current_time = pd.to_datetime(datetime.now())
            #print(current_time)
            print('Updating store with new energy data')
            print(f'stored_df has {len(stored_df)} lines')
            complete_df = pd.concat([stored_df, energyData], sort=True)
            complete_df = complete_df.iloc[len(energyData):]
            # print(f'complete_df has {len(complete_df)} lines')
    # print('Storing data')
    json_data = complete_df.to_json(date_format='iso')

    return json_data



@app.callback(
    Output('Energy_bilan', 'figure'),
    [Input('energydata','data')],
    [State('energydata', 'data')])
def update_EnegryBilan(refresh, data):
    import plotly.graph_objects as go
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            fig=PlottingTools.Energy_bilanPlot(data, OFFSET)
    return fig

#%%
app.run_server(debug=False)





import importlib
importlib.reload(PlottingTools)




