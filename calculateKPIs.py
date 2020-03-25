# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 14:05:52 2019

@author: NINIC2
"""
import numpy as np
import pandas as pd

from datetime import datetime, timedelta


# Calculates common statistical properties
def stats(df_column, rate=False):
    value_min = df_column.min()
    value_max = df_column.max()
    value_avg = df_column.mean()
    if not rate:
        value_tot = df_column.sum()
    else:
        # Expecting a rate per minute (e.g. L/min) and logging per 10 sec
        value_tot = value_avg * len(df_column) / 60 * 10
    return value_min, value_max, value_avg, value_tot


def integrate_flow(df_column):
    threshold_time = pd.to_datetime(datetime.utcnow() - timedelta(hours=24)).tz_localize('UTC')
    df_column = df_column[df_column.index > threshold_time]
    df_column.fillna(method='ffill', inplace=True)
    df2 = pd.DataFrame.from_dict({'Time': df_column.index})
    y = df_column.tolist()
    mean_y = np.array([(a + b) / 2 for a, b in zip(y[:-1], y[1:])])

    delta_x = pd.to_timedelta(df2['Time'].diff(1)).dt.total_seconds()
    delta_x = delta_x.iloc[1:]
    df3 = pd.DataFrame.from_dict({
        'delta_x': delta_x,
        'mean_y': mean_y,
    })
    df3['product'] = df3['delta_x'] * df3['mean_y']
    cumul = df3['product'].sum()
    return cumul


# Calculates common statistical properties
def stats_24(df_column):
    threshold_time = pd.to_datetime(datetime.utcnow() - timedelta(hours=24)).tz_localize('UTC')
    df_column = df_column[df_column.index > threshold_time]
    mean_24 = df_column.mean()
    val_now = df_column.dropna().iloc[-1]
    return val_now, mean_24


# Calculates statistical properties of each peak above a predefined threshold
def peak_stats(df_column, threshold):
    # Get values as a list
    var_temp = df_column.dropna()
    var = var_temp.tolist()

    # Get timestamp as a list
    time_temp = var_temp.reset_index()
    time_temp = time_temp['index']
    time = []

    for date in time_temp:
        time.append(np.datetime64(date))
    # Get indexes of the values above threshold
    var_high_indx = [ind for ind, x in enumerate(var) if x > threshold]

    # Locate jumps
    var_jump = [indx_2 - indx_1 for indx_1, indx_2 in zip(var_high_indx, var_high_indx[1:])]

    # Calculate average of the variable when var is higher than the specified threshold
    buffer = []
    var_avg = []
    time_avg = []
    fAE_val = []
    cycle_time = 30
    for i in np.arange(0, len(var_jump) - 1, 1).tolist():
        if var_jump[i] == 1:
            buffer.append(var[var_high_indx[i]])
        else:
            buffer.append(var[var_high_indx[i]])
            var_avg.append(sum(buffer) / len(buffer))
            time_avg.append(time[var_high_indx[i] - round(len(buffer) / 2)])
            fAE_val.append((cycle_time-var_jump[i]+1)/cycle_time)
            buffer = []

    # Create a new dataframe and return it
    peak_avg = pd.DataFrame(list(zip(time_avg, var_avg, fAE_val)), columns=['datetime', df_column.name + '-avg cycle', df_column.name+'-fAE'])
    peak_avg.set_index('datetime', inplace=True)
    peak_avg.index = peak_avg.index.tz_localize("UTC")

    # Calculate the average for the entire dataframe
    if len(var_avg) != 0:
        peak_avg_overall = sum(var_avg) / len(var_avg)
    else:
        peak_avg_overall = 0

    return peak_avg_overall, peak_avg
