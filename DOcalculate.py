from datetime import datetime, timedelta
import pandas as pd
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

df=pd.read_csv('datEAUbase_download.csv')


OFFSET = 60  # weeks

end_time, start_time = (
	pd.to_datetime(
		datetime.utcnow() - timedelta(weeks=OFFSET)
	).tz_localize("UTC"),
	pd.to_datetime(
		datetime.utcnow() - timedelta(weeks=OFFSET) - timedelta(seconds=INTERVAL_LENGTH_SEC)
	).tz_localize("UTC"))

end_string = datetime.strftime(end_time, TIME_FORMAT)
start_string = datetime.strftime(start_time, TIME_FORMAT)


# energy calculation


extract_energy = Energy_shopping_list(start_string, end_string)
energyDataorg = Dateaubase.extract_data(engine, extract_energy)
energyDataorg .fillna(inplace=True, method='ffill')
energyData =  energyDataorg.groupby(pd.Grouper(freq='1d')).mean()*3600
energyData['pilEAUte-Pilote sludge recycle-FIT_260-Flowrate (Liquid)']=energyData['pilEAUte-Pilote sludge recycle-FIT_260-Flowrate (Liquid)']/3600
energyData .fillna(inplace=True, method='ffill')