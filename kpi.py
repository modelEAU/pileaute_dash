# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 14:05:52 2019

@author: NINIC2
"""
import numpy as np
import pandas as pd
import Dateaubase


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

# Calculates statistical properties of each peak above a predefined threshold


def peak_stats(df_column, treshold):
    # Get values as a list
    var_temp = df_column.dropna()
    var = var_temp.tolist()

    # Get timestamp as a list
    time_temp = var_temp.reset_index()
    time_temp = time_temp['datetime']
    time = [Dateaubase.date_to_epoch(date) for date in time_temp]

    # Get indexes of the values above treshold
    var_high_index = [ind for ind, x in enumerate(var) if x > treshold]

    # Locate jumps
    var_jump = [index_2 - index_1 for index_1, index_2 in zip(var_high_index, var_high_index[1:])]

    # Calculate average of the variable when var is higher than the specified treshold
    buffer = []
    var_avg = []
    time_avg = []
    for i in np.arange(0, len(var_jump) - 1, 1).tolist():
        if var_jump[i] == 1:
            buffer.append(var[var_high_index[i]])
        else:
            buffer.append(var[var_high_index[i]])
            var_avg.append(sum(buffer) / len(buffer))
            time_avg.append(time[var_high_index[i] - round(len(buffer) / 2)])
            buffer = []

    # Convert epoch time to datetime type
    time_avg = [Dateaubase.epoch_to_pandas_datetime(dateTime) for dateTime in time_avg]

    # Create a new dataframe and return it
    peak_avg = pd.DataFrame(
        list(zip(time_avg, var_avg)),
        columns=['datetime', df_column.name + ' - avg cycle']
    )
    peak_avg.set_index('datetime', inplace=True)

    # Calculate the average for the entire dataframe
    if len(var_avg) != 0:
        peak_avg_overall = sum(var_avg) / len(var_avg)
    else:
        peak_avg_overall = 0

    return peak_avg_overall, peak_avg
