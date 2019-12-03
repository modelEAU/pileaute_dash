from itertools import cycle

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
from matplotlib import cm
from pandas.plotting import register_matplotlib_converters
from plotly import tools

COLOR_PALETTE = [
    'rgb(31, 119, 180)',    # blue
    'rgb(255, 127, 14)',    # orange
    'rgb(44, 160, 44)',    # green
    'rgb(214, 39, 40)',     # red
    'rgb(148, 103, 189)',   # purple
    'rgb(140, 86, 75)',     # taupe
    'rgb(227, 119, 194)',   # pink
    'rgb(127, 127, 127)',   # middle grey
    'rgb(188, 189, 34)',    # greenish yellow
    'rgb(23, 190, 207)']    # azure

def plotRaw_D_mpl(df):
    register_matplotlib_converters()

    _, ax = plt.subplots(figsize=(12, 8))

    names = []
    for column in df.columns:
        equipment = column.split('-')[-3]
        parameter = column.split('-')[-2]
        unit = column.split('-')[-1]
        name = " ".join([equipment, parameter, unit])
        names.append(name)
        ax.plot(df[column])

    plt.legend(names)
    plt.xticks(rotation=45)
    plt.ylim(bottom=0)
    plt.title("Raw data")
    plt.show(block=False)

def plotRaw_D_plotly(df):
    traces = []
    axes = []
    colors = []
    color_cycle = cycle(COLOR_PALETTE)
    dash_styles = ['solid', 'dash', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    dash_cycle = cycle(dash_styles)

    for column in df.columns:
        project, location, equipment, parameter, unit = column.split('-')
        name = '{} ({})'.format(parameter, unit)
        if name not in axes:
            axes.append(name)
            del dash_cycle
            dash_cycle = cycle(dash_styles)
        else:
            pass
        trace = go.Scattergl(
            x=df.index,
            y=df[column],
            yaxis='y{}'.format(axes.index(name) + 1),
            name='{}-{} ({})'.format(equipment, parameter, unit),
            mode='lines+markers',
            line=dict(
                dash=next(dash_cycle)
            ),
            marker=dict(
                opacity=0
            ),
        )
        traces.append(trace)

    n_axes = len(axes)
    layout_axes = []
    ax_pos = 0
    for i in range(n_axes):
        color = next(color_cycle)
        '''anchor='free',
        overlaying='y',
        side='left',
        position=0.15'''
        ax_pos = i * 0.075
        layout_axes.append({
            'yaxis{}'.format(i + 1): dict(
                title=axes[i],
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                ),
                anchor='free',
                side='left',
                position=ax_pos
            )
        })
    layout = {
        'title': 'Raw uploaded data',
        'xaxis': {
            'domain': [0.075 * (n_axes - 1), 1],
            'title': 'Date and time'
        }
    }
    for ax in layout_axes:
        layout = {**layout, **ax}

    figure = go.Figure(data=traces, layout=layout)
    return figure


def plotUnivar_mpl(channel):
    register_matplotlib_converters()

    _, ax = plt.subplots(figsize=(12, 8))

    raw = channel.raw_data

    plt.plot(raw)

    if channel.processed_data is not None:
        for col in channel.processed_data.columns:
            if col in ['filled', 'sorted', 'resampled']:
                plt.plot(channel.processed_data[col])

    if channel.calib is not None:
        calib_start = pd.to_datetime(channel.calib['start'])
        calib_end = pd.to_datetime(channel.calib['end'])
        most_recent = channel.info['last-processed']
        if most_recent == 'raw':
            df = channel.raw_data
        else:
            df = channel.processed_data
        plt.plot(df[most_recent][calib_start:calib_end])

    plt.title('Data preparation')
    plt.ylabel('Value'),
    plt.xlabel('Date and Time')
    plt.show(block=False)

def plotUnivar_plotly(channel):
    traces = []
    raw = channel.raw_data
    trace = go.Scattergl(
        x=raw.index,
        y=raw['raw'],
        name='Raw data',
        mode='lines+markers',
        marker=dict(
            opacity=0
        )
    )
    traces.append(trace)

    if channel.processed_data is not None:
        for col in channel.processed_data.columns:
            if col in ['filled', 'sorted', 'resampled']:
                trace = go.Scattergl(
                    x=channel.processed_data.index,
                    y=channel.processed_data[col],
                    name=col,
                    mode='lines+markers',
                    marker=dict(
                        opacity=0
                    ),
                )
                traces.append(trace)

    if channel.calib is not None:
        calib_start = pd.to_datetime(channel.calib['start'])
        calib_end = pd.to_datetime(channel.calib['end'])
        most_recent = channel.info['last-processed']
        if most_recent == 'raw':
            df = channel.raw_data
        elif channel.processed_data is not None:
            df = channel.processed_data
        else:
            df = channel.raw_data
            most_recent = 'raw'
        trace = go.Scattergl(
            x=df[calib_start:calib_end].index,
            y=df[calib_start:calib_end][most_recent],
            name='Calibration series',
            mode='lines+markers',
            marker=dict(
                opacity=0
            ),
        )
        traces.append(trace)

    layout = go.Layout(
        dict(
            title='Data preparation',
            yaxis=dict(title='Value'),
            xaxis=dict(title='Date and Time')
        )
    )
    figure = go.Figure(data=traces, layout=layout)
    return figure

def plotOutliers_mpl(channel):
    register_matplotlib_converters()

    _, ax = plt.subplots(figsize=(12, 8))
    filtration_method = channel.info['current_filtration_method']
    df = channel.filtered[filtration_method].copy(deep=True)
    df.index.name = 'index'
    df.reset_index(inplace=True, drop=False)
    df.index.name = 'index'
    df['t'] = df['index'].apply(lambda x: pd.Timestamp(str(x)))
    df.set_index(df['t'], drop=True)

    raw = channel.raw_data.copy(deep=True)
    raw.index.name = 'index'
    raw.reset_index(inplace=True, drop=False)
    raw.index.name = 'index'
    raw['t'] = raw['index'].apply(lambda x: pd.Timestamp(str(x)))
    raw.set_index(raw['t'], drop=True)
    raw_out = raw.join(df['outlier'], how='left').dropna()

    AD = df['Accepted']
    outlier = raw_out['raw'].loc[raw_out['outlier']]

    ub = df['UpperLimit_outlier']
    lb = df['LowerLimit_outlier']

    legend_list = []
    ax.plot(raw.index, raw['raw'], 'grey', 'o')
    legend_list.append('Raw')
    ax.plot(outlier, 'rx')
    legend_list.append('Outliers')
    ax.plot(df.index, lb, 'b')
    legend_list.append('Lower bound')
    ax.plot(df.index, ub, 'r')
    legend_list.append('Upper bound')
    ax.plot(df.index, AD, 'orange')
    legend_list.append('Accepted')
    if 'Smoothed_AD' in df.columns:
        smooth = df['Smoothed_AD']
        ax.plot(df.index, smooth, 'g')
        legend_list.append('Smooth')

    plt.xlabel('Time')
    plt.xticks(rotation=45)
    plt.ylabel(channel.parameter)

    plt.legend(legend_list)
    plt.show(block=False)

def plotOutliers_plotly(channel):
    filtration_method = channel.info['current_filtration_method']
    df = channel.filtered[filtration_method]
    raw = channel.raw_data['raw']
    AD = df['Accepted']
    raw_out = channel.raw_data.join(df['outlier'], how='left').dropna()
    outlier = raw_out['raw'].loc[raw_out['outlier']]

    ub = df['UpperLimit_outlier']
    lb = df['LowerLimit_outlier']

    to_plot = {
        'Raw': raw,
        'Upper Bound': ub,
        'Lower Bound': lb,
        'Accepted': AD,
        'Outliers': outlier
    }
    if 'Smoothed_AD' in df.columns:
        to_plot['Smooth'] = df['Smoothed_AD']

    traces = []
    for name, series in to_plot.items():

        trace = go.Scattergl(
            x=series.index,
            y=series,
            name=name
        )
        if name == 'Accepted':
            trace['mode'] = 'lines+markers'
            trace['marker'] = dict(opacity=0, color='rgb(255, 127, 14)')  # orange
        elif name == 'Upper Bound':
            trace['mode'] = 'lines+markers'
            trace['marker'] = dict(opacity=0, color='rgb(214, 39, 40)')  # red
        elif name == 'Lower Bound':
            trace['mode'] = 'lines+markers'
            trace['marker'] = dict(opacity=0, color='rgb(31, 119, 180)')  # blue
        elif name == 'Smooth':
            trace['mode'] = 'lines+markers'
            trace['marker'] = dict(opacity=0, color='rgb(44, 160, 44)')  # green
        elif name == 'Raw':
            trace['mode'] = 'markers'
            trace['marker'] = dict(opacity=0.8, color='rgb(127, 127, 127)', size=2)  # grey
        elif name == 'Outliers':
            trace['mode'] = 'markers'
            trace['marker'] = dict(opacity=1, color='black', size=8, symbol='x')
        traces.append(trace)

    layout = go.Layout(
        dict(
            title='Outlier Detection',
            yaxis=dict(title='Value'),
            xaxis=dict(title='Date and Time')
        )
    )
    figure = go.Figure(data=traces, layout=layout)
    return figure

def plotDScore_mpl(channel):
    _, axes = plt.subplots(figsize=(12, 8), nrows=4, ncols=1)
    # This function allows to create several plots with the data feature.
    # For each data features, you need to change the limits. The whole are
    # defined in the DefaultParam function.
    # GRAPHICS
    axes_list = axes.flatten()

    filtration_method = channel.info['current_filtration_method']
    df = channel.filtered[filtration_method].copy(deep=True)

    df.reset_index(inplace=True)
    df['t'] = df['index'].apply(lambda x: pd.Timestamp(str(x)))
    df.set_index(df['t'], drop=True)

    params = channel.params

    corr_max = params['fault_detection_uni']['corr_max']
    corr_min = params['fault_detection_uni']['corr_min']

    slope_max = params['fault_detection_uni']['slope_max']
    slope_min = params['fault_detection_uni']['slope_min']

    std_max = params['fault_detection_uni']['std_max']
    std_min = params['fault_detection_uni']['std_min']

    range_max = params['fault_detection_uni']['range_max']
    range_min = params['fault_detection_uni']['range_max']

    ax0 = axes_list[0]
    ax0.plot(df['Q_corr'], linewidth=2)
    ax0.set(ylabel='Runs test value')

    ax0.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [corr_max, corr_max],
        c='r',
        linewidth=1)
    ax0.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [corr_min, corr_min],
        c='r',
        linewidth=1)
    ax0.set_xticks([])

    ax1 = axes_list[1]
    ax1.plot(df['Q_slope'], linewidth=2)

    ax1.set(ylabel='Slope [mg/L*s]')
    ax1.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [slope_max, slope_max],
        c='r',
        linewidth=1)
    ax1.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [slope_min, slope_min],
        c='r',
        linewidth=1)
    ax1.set_xticks([])

    ax2 = axes_list[2]
    ax2.plot(df['Q_std'], linewidth=2)
    ax2.set(ylabel='Std ln[mg/L]')
    ax2.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [std_max, std_max],
        c='r',
        linewidth=1)
    ax2.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [std_min, std_min],
        c='r',
        linewidth=1)
    ax2.set_xticks([])

    ax3 = axes_list[3]
    ax3.plot(df['Smoothed_AD'], linewidth=2)
    ax3.set(ylabel='Range [mg/L]')
    ax3.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [range_max, range_max],
        c='r',
        linewidth=1)
    ax3.plot(
        [df.first_valid_index(), df.last_valid_index()],
        [range_min, range_min],
        c='r',
        linewidth=1)
    ax3.set_xticks([])

    plt.show(block=False)

def plotTreatedD_plotly(channel):
    filtration_method = channel.info['current_filtration_method']
    df = channel.filtered[filtration_method]
    raw = channel.raw_data['raw']
    treated = df['treated']
    deleted = df['deleted']
    to_plot = {
        'Raw': raw,
        'Treated': treated,
        'Deleted': deleted,
    }
    traces = []
    for name, series in to_plot.items():
        trace = go.Scattergl(
            x=series.index,
            y=series,
            name=name
        )
        if name == 'Treated':
            trace['mode'] = 'lines+markers'
            trace['marker'] = dict(opacity=0, color='rgb(44, 160, 44)')  # green
        elif name == 'Deleted':
            trace['mode'] = 'lines+markers'
            trace['marker'] = dict(opacity=0, color='rgb(214, 39, 40)')  # red
        elif name == 'Raw':
            trace['mode'] = 'markers'
            trace['marker'] = dict(opacity=0.8, color='rgb(127, 127, 127)', size=5)  # grey
        traces.append(trace)

    layout = go.Layout(
        dict(
            title='Treated univariate data',
            yaxis=dict(title='Value'),
            xaxis=dict(title='Date and Time')
        )
    )
    figure = go.Figure(data=traces, layout=layout)
    return figure

def plotTreatedD_mpl(channel):
    filtration_method = channel.info['current_filtration_method']

    raw = channel.raw_data['raw'].copy(deep=True)
    df = channel.filtered[filtration_method][['treated', 'deleted']].copy(deep=True)
    df.index.name = 'index'
    df.reset_index(inplace=True, drop=False)
    df.index.name = 'index'
    df['t'] = df['index'].apply(lambda x: pd.Timestamp(str(x)))
    df.set_index(df['t'], drop=True)

    raw = channel.raw_data.copy(deep=True)
    raw.index.name = 'index'
    raw.reset_index(inplace=True, drop=False)
    raw.index.name = 'index'
    raw['t'] = raw['index'].apply(lambda x: pd.Timestamp(str(x)))
    raw.set_index(raw['t'], drop=True)

    treated = df['treated']
    deleted = df['deleted']
    _, ax = plt.subplots(figsize=(12, 8))
    # This function allows to plot the DataValidated with also the raw data
    ax.plot(raw.index, raw['raw'], 'k')
    ax.plot(treated, '-g', markersize=6, markerfacecolor='g')
    ax.plot(deleted, 'r', markersize=6, markerfacecolor='r')
    ax.set(xlabel='Time')
    plt.xticks(rotation=45)
    ax.set(ylabel=channel.parameter)
    plt.legend(['Raw', 'Treated', 'Deleted'])
    plt.show(block=False)

def plotD_plotly(params, testID, start=None, end=None, channel=None):
    # This function allows to create several plots with the data feature.
    # For each data features, you need to change the limits. The whole are
    # defined in the DefaultParam function.
    if channel:
        filtration_method = channel.info['current_filtration_method']
        df = channel.filtered[filtration_method]
        start = df.first_valid_index()
        end = df.last_valid_index()

    min_val = params[0]
    max_val = params[1]
    titles = {
        'Q_corr': 'Runs test',
        'Q_slope': 'Slope test',
        'Q_std': 'Standard deviation test',
        'Q_range': 'Data range test'
    }
    # if testID == 'Q_std':
    #     min_val = 10 ** min_val
    #     max_val = 10 ** max_val

    # DEFINING VARIABLES
    traces = []
    trace1a = go.Scattergl(
        x=[start, end],
        y=[min_val, min_val],
        xaxis='x1',
        yaxis='y1',
        name='Min. threshold',
        mode='lines',
        line=dict(
            color=('rgb(205, 12, 24)'),
            width=1,
        )
    )
    traces.append(trace1a)
    trace1b = go.Scattergl(
        x=[start, end],
        y=[max_val, max_val],
        xaxis='x1',
        yaxis='y1',
        mode='lines',
        name='Max. threshold',
        line=dict(
            color=('rgb(205, 12, 24)'),
            width=1,
        )
    )
    traces.append(trace1b)
    if channel:
        if testID in df.columns:
            if testID == 'Q_range':
                name = 'Smoothed_AD'
            else:
                name = testID
            trace1c = go.Scattergl(
                x=df.index,
                y=df[name],
                xaxis='x1',
                yaxis='y1',
                name=name,
                mode='lines',
                line=dict(
                    color=('rgb(22, 96, 167)'),
                    width=2,
                )
            )
            traces.append(trace1c)

    layout = go.Layout(
        title=titles[testID],
        autosize=True,
        # width=800,
        height=250,
        margin=go.layout.Margin(
            l=50,
            r=50,
            b=50,
            t=50,
            pad=4
        ),
        xaxis=dict(
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
    )

    figure = go.Figure(layout=layout, data=traces)
    # if testID == 'Q_std':
    #     figure.update(dict(layout=dict(yaxis=dict(type='log'))))
    return figure

def ini_multivar_plotly(df, start=None, end=None):
    traces = []
    axes = []
    colors = []
    color_cycle = cycle(COLOR_PALETTE)
    dash_styles = ['solid', 'dash', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    dash_cycle = cycle(dash_styles)
    for column in df.columns:
        series, project, location, equipment, parameter, unit = column.split('-')
        name = '{} ({})'.format(parameter, unit)
        if name not in axes:
            axes.append(name)
            del dash_cycle
            dash_cycle = cycle(dash_styles)
        else:
            pass
        trace = go.Scattergl(
            x=df[column].index,
            y=df[column],
            yaxis='y{}'.format(axes.index(name) + 1),
            name='{}: {}-{} ({})'.format(series, equipment, parameter, unit),
            mode='lines+markers',
            line=dict(
                dash=next(dash_cycle)
            ),
            marker=dict(
                opacity=0
            )
        )
        traces.append(trace)
    n_axes = len(axes)
    layout_axes = []
    ax_pos = 0
    for i in range(n_axes):
        color = next(color_cycle)
        '''anchor='free',
        overlaying='y',
        side='left',
        position=0.15'''
        ax_pos = i * 0.10
        layout_axes.append({
            'yaxis{}'.format(i + 1): dict(
                title=axes[i],
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                ),
                anchor='free',
                side='left',
                position=ax_pos
            )
        })
    layout = {
        'title': 'Multivariate data preparation',
        'xaxis': {
            'domain': [0.10 * (n_axes - 1), 1],
            'title': 'Date and time'
        }
    }
    for ax in layout_axes:
        layout = {**layout, **ax}
    if start is not None and end is not None:
        calib_shape = {
            'type': 'rect',
            'xref': 'x',
            'yref': 'paper',
            'x0': start,
            'x1': end,
            'y0': 0,
            'y1': 1,
            'line': {
                'color': 'rgba(214, 39, 40, 1)',
                'width': 1
            },
            'fillcolor': 'rgba(214, 39, 40, 0.3)'
        }
        layout['shapes'] = [calib_shape]
    figure = go.Figure(layout=layout, data=traces)
    return figure


def show_pca_plotly(df, limits):
    traces = []
    if 'pc_1' not in df.columns or 'pc_2' not in df.columns:
        figure = go.Figure(data=[])
    else:
        
        start_cal = pd.Timestamp(limits['start_cal'])
        end_cal = pd.Timestamp(limits['end_cal'])

        start = df.first_valid_index().replace(tzinfo=None)
        end = df.last_valid_index().replace(tzinfo=None)
        print(start, type(start))
        print(start_cal, type(start_cal))
        x1 = df.loc[start_cal: end_cal, 'pc_1']
        y1 = df.loc[start_cal: end_cal, 'pc_2']

        x0_a = df.loc[start:start_cal, 'pc_1']
        y0_a = df.loc[start:start_cal, 'pc_2']

        x0_b = df.loc[end_cal:end, 'pc_1']
        y0_b = df.loc[end_cal:end, 'pc_2']

        x0 = pd.concat([x0_a, x0_b])
        y0 = pd.concat([y0_a, y0_b])

        trace1 = go.Scattergl(
            x=x1,
            y=y1,
            mode='markers',
            name='Calibration'
        )
        trace0 = go.Scattergl(
            x=x0,
            y=y0,
            mode='markers',
            name='Rest'
        )
        traces = [trace0, trace1]

        ellipse_a = np.sqrt(limits['T2']) * limits['pc_std'][0]
        ellipse_b = np.sqrt(limits['T2']) * limits['pc_std'][1]

        layout = go.Layout(
            shapes=[
                dict(
                    type='circle',
                    xref='x',
                    yref='y',
                    x0=ellipse_a * -1,
                    x1=ellipse_a,
                    y0=ellipse_b * -1,
                    y1=ellipse_b,
                    line=dict(
                        color='rgba(214, 39, 40, 1)',
                        width=1
                    ),
                    fillcolor='rgba(214, 39, 40, 0.3)'
                )
            ],
            title='Principal component scatter plot',
            xaxis=dict(
                title='PC 1',
                range=[ellipse_a * -3, ellipse_a * 3]
            ),
            yaxis=dict(
                title='PC 2',
                range=[ellipse_b * -3, ellipse_b * 3]
            ),
        )
        figure = go.Figure(data=traces, layout=layout)
        return figure


def show_q_residuals_plotly(df, limits):
    Q_lim = limits['Q']
    start = df.first_valid_index()
    end = df.last_valid_index()
    traces = []
    if 'Q' not in df.columns:
        layout = go.Layout(
            title='PCA model residuals',
            yaxis=dict(
                title='Q (normalised units)'
            ),
            xaxis=dict(
                title='Date and time'
            )
        )
    else:
        '''trace0 = go.Scattergl(
            x=[start, end],
            y=[Q_lim, Q_lim],
            mode='lines',
            line=dict(
                dash='dashdot',
                color=COLOR_PALETTE[3]  # red
            ),
        ),
        traces.append(trace0)'''

        y1 = df['Q'].loc[df['Q'] <= Q_lim]
        x1 = y1.index
        trace1 = go.Scattergl(
            x=x1,
            y=y1,
            name='Accepted',
            mode='markers',
            marker=dict(
                color=COLOR_PALETTE[2],
                symbol='circle'
            ),
        )
        traces.append(trace1)

        y2 = df['Q'].loc[df['Q'] > Q_lim]
        x2 = y2.index
        trace2 = go.Scattergl(
            x=x2,
            y=y2,
            name='Rejected',
            mode='markers',
            marker=dict(
                color=COLOR_PALETTE[1],
                symbol='x'
            ),
        )
        traces.append(trace2)

        if Q_lim is None:
            layout = go.Layout(
                title='PCA model residuals',
                yaxis=dict(
                    title='Q (normalised units)',
                ),
                xaxis=dict(title='Date and time'),

                shapes=[{
                    'type': 'line',
                    'xref': 'x',
                    'x0': start,
                    'x1': end,
                    'y0': Q_lim,
                    'y1': Q_lim,
                    'line': {
                        'color': COLOR_PALETTE[3],
                        'dash': 'dashdot',
                        'width': 2
                    },
                }],
            )
        else:
            layout = go.Layout(
                title='PCA model residuals',
                yaxis=dict(
                    title='Q (normalised units)',
                    range=[0, 3 * Q_lim]
                ),
                xaxis=dict(title='Date and time'),

                shapes=[{
                    'type': 'line',
                    'xref': 'x',
                    'x0': start,
                    'x1': end,
                    'y0': Q_lim,
                    'y1': Q_lim,
                    'line': {
                        'color': COLOR_PALETTE[3],
                        'dash': 'dashdot',
                        'width': 2
                    },
                }],
            )

    figure = go.Figure(layout=layout, data=traces)
    return figure

def show_pca_mpl(df, limits):
    fig, ax = plt.subplots(figsize=(10, 10), nrows=1, ncols=1)
    plt.rc('lines', linewidth=1)
    color = iter(cm.plasma(np.linspace(0, 1, 4)))
    start = limits['start_cal']
    end = limits['end_cal']
    ax.plot(df['pc_1'], df['pc_2'], 'o', markersize=0.5, c=next(color))
    ax.plot(
        df['pc_1'].loc[start:end],
        df['pc_2'].loc[start:end],
        'o', markersize=0.5, c=next(color)
    )
    ax.set(
        ylabel='PC 2',
        xlabel='PC 1',
        title='Principal components of calibration and complete data sets'
    )
    # ### drawing the ellipse

    ellipse_a = np.sqrt(limits['T2']) * limits['pc_std'][0]
    ellipse_b = np.sqrt(limits['T2']) * limits['pc_std'][1]
    t = np.linspace(0, 2 * np.pi, 100)

    ax.plot(ellipse_a * np.cos(t), ellipse_b * np.sin(t), c=next(color))
    ax.grid(which='major', axis='both')
    ax.legend(['complete', 'calibration', 'limit {}'.format(limits['alpha'])])
    plt.gca().set_aspect('equal')
    plt.show()

def show_multi_output_mpl(df):
    register_matplotlib_converters()
    cols_list = []
    for column in df.columns:
        if 'raw' in column or 'treated' in column:
            cols_list.append(column)
    fig, axes = plt.subplots(figsize=(20, 10), nrows=len(cols_list) + 1, ncols=1)
    plt.rc('lines', linewidth=0.5)
    color = iter(cm.plasma(np.linspace(0.05, 0.8, len(cols_list) + 1)))

    fig.subplots_adjust(hspace=0.5)
    fig.suptitle('Output of multivariate filter')
    axes_array = np.array(axes).flatten()
    for ax, feature in zip(axes_array, cols_list):

        ax.plot(df.index, df[feature], c=next(color))
        ax.set(ylabel=feature.split(' ')[0].upper())
        ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)

    ax = axes_array[-1]
    ax.plot(df.index, df['fault_count'], c='k')
    ax.set(ylabel='fault count', xlabel='Date')
    ax.set_xticklabels(df.index, rotation=45)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    plt.show()

def show_multi_output_plotly(data):
    traces = []
    if 'fault_count' not in data.columns:
        figure = go.Figure(data=[])
    else:
        cols_list = []
        for column in data.columns:
            if 'raw' in column or 'treated' in column:
                cols_list.append(column)
        df = data[cols_list]
        traces = []
        axes = []
        colors_alpha = []
        for color in COLOR_PALETTE:
            color.replace('rgb', 'rgba')
            c0 = color.replace(')', ', 1)')
            c1 = color.replace(')', ', 0.5)')
            c2 = color.replace(')', ', 0.1)')
            color = [c0, c1, c2]
            colors_alpha.append(color)
        color_alpha_cycle = cycle(colors_alpha)
        max_faults = data['fault_count'].max()
        symbol_styles = ['x', 'square', 'triangle-up', 'circle', 'star']
        symbol_cycle = cycle(symbol_styles)
        dash_styles = ['solid', 'dash', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
        dash_cycle = cycle(dash_styles)
        for column in df.columns:
            series, project, location, equipment, parameter, unit = column.split('-')
            name = '{} ({})'.format(parameter, unit)
            if name not in axes:
                axes.append(name)
                del dash_cycle
                dash_cycle = cycle(dash_styles)
                colors = next(color_alpha_cycle)
                colors = cycle(colors)
            else:
                pass
            for i in range(data.fault_count.max() + 1):
                trace = go.Scattergl(
                    x=df[column].loc[data.fault_count == i].index,
                    y=df[column].loc[data.fault_count == i],
                    yaxis='y{}'.format(axes.index(name) + 1),
                    name='F{} {}: {}-{} ({})'.format(i, series, equipment, parameter, unit),
                    mode='markers',
                    marker=dict(
                        symbol=next(symbol_cycle),
                        color=(next(colors)),
                        size=6
                    ),
                )
                traces.append(trace)
        n_axes = len(axes)
        layout_axes = []
        ax_pos = 0
        color_alpha_cycle = cycle(colors_alpha)
        for i in range(n_axes):
            colors = next(color_alpha_cycle)
            '''anchor='free',
            overlaying='y',
            side='left',
            position=0.15'''
            ax_pos = i * 0.10
            layout_axes.append({
                'yaxis{}'.format(i + 1): dict(
                    title=axes[i],
                    titlefont=dict(
                        color=colors[0]
                    ),
                    tickfont=dict(
                        color=colors[0]
                    ),
                    anchor='free',
                    side='left',
                    position=ax_pos
                )
            })
        layout = {
            'title': 'Multivariate data preparation',
            'xaxis': {
                'domain': [0.10 * (n_axes - 1), 1],
                'title': 'Date and time'
            }
        }
        for ax in layout_axes:
            layout = {**layout, **ax}
        figure = go.Figure(layout=layout, data=traces)
        return figure
def extract_plotly(df):
    traces = []
    axes = []
    colors = []
    color_cycle = cycle(COLOR_PALETTE)
    dash_styles = ['solid', 'dash', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    dash_cycle = cycle(dash_styles)

    for column in df.columns:
        project, location, equipment, parameter, unit = column.split('-')
        name = '{} ({})'.format(parameter, unit)
        if name not in axes:
            axes.append(name)
            del dash_cycle
            dash_cycle = cycle(dash_styles)
        else:
            pass
        trace = go.Scattergl(
            x=df.index,
            y=df[column],
            yaxis='y{}'.format(axes.index(name) + 1),
            name='{}-{} ({})'.format(equipment, parameter, unit),
            mode='lines+markers',
            line=dict(
                dash=next(dash_cycle)
            ),
            marker=dict(
                opacity=0
            ),
        )
        traces.append(trace)

    n_axes = len(axes)
    layout_axes = []
    ax_pos = 0
    for i in range(n_axes):
        color = next(color_cycle)
        '''anchor='free',
        overlaying='y',
        side='left',
        position=0.15'''
        ax_pos = i * 0.075
        layout_axes.append({
            'yaxis{}'.format(i + 1): dict(
                title=axes[i],
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                ),
                anchor='free',
                side='left',
                position=ax_pos
            )
        })
    layout = {
        'title': 'Data to extract',
        'xaxis': {
            'domain': [0.075 * (n_axes - 1), 1],
            'title': 'Date and time'
        }
    }
    for ax in layout_axes:
        layout = {**layout, **ax}

    figure = go.Figure(data=traces, layout=layout)

    return figure
