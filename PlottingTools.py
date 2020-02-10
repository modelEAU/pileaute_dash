from itertools import cycle

import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

COLORWAY = ['#f3cec9', '#e7a4b6', '#cd7eaf', '#a262a9', '#6f4d96', '#3d3b72', '#182844']


def extract_plotly(df):
    traces = []
    axes = []
    n_cols = len(df.columns)
    color_cycle = cycle(COLORWAY[:n_cols])
    dash_styles = ['solid', 'dash', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    dash_cycle = cycle(dash_styles[:n_cols])

    for column in df.columns:
        _, _, equipment, parameter = column.split('-')
        name = f'{equipment} {parameter}'
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
            name=f'{equipment} {parameter}',
            mode='lines+markers',
            line=dict(
                dash=next(dash_cycle),
                color=next(color_cycle)
            ),
            marker=dict(
                opacity=0,
            ),
        )
        traces.append(trace)

    n_axes = len(axes)
    layout_axes = []
    ax_pos = 0
    for i in range(len(df.columns)):
        color = next(color_cycle),
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
        },
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)'
    }
    for ax in layout_axes:
        layout = {**layout, **ax}

    figure = go.Figure(data=traces, layout=layout)

    return figure


def avn_plot(df):
    df = df.groupby(pd.Grouper(freq='300S')).first()
    df.index = df.index.tz_convert('US/Eastern')
#   df = df[df['pilEAUte-Pilote effluent-Varion_002-NH4_N'].notnull()]
    fig = go.Figure()
    # NH4
    trace_nh4 = go.Scattergl(
        x=df.index,
        y=df['pilEAUte-Pilote effluent-Varion_002-NH4_N'] * 1000,
        name='Ammonia',
        mode='lines',
        yaxis='y',
        line=dict(
            dash='solid',
            color='blue'
        ),
    )
    fig.add_trace(trace_nh4)

    # NO3
    trace_no3 = go.Scattergl(
        x=df.index,
        y=df['pilEAUte-Pilote effluent-Varion_002-NO3_N'] * 1000,
        name='Nitrate',
        mode='lines',
        yaxis='y',
        line=dict(
            dash='solid',
            color='turquoise'
        ),
    )
    fig.add_trace(trace_no3)
    # AvN
    trace_avn = go.Scattergl(
        x=df.index,
        y=df['pilEAUte-Pilote effluent-Varion_002-NH4_N']
        / df['pilEAUte-Pilote effluent-Varion_002-NO3_N'],
        name='AvN ratio',
        yaxis='y2',
        mode='lines+markers',
        line=dict(
            dash='solid',
            color='orange'
        ),
        marker={
            'opacity': 0
        }
    )
    fig.add_trace(trace_avn)

    # layout
    layout_axes = []
    name_axes = ['y1', 'y2']
    title_axes = ['Nitrogen (mg/l)', 'AvN ratio']
    n_axes = len(name_axes)

    for i in range(len(name_axes)):
        ax_pos = i * 0.075
        layout_axes.append({
            'title': title_axes[i],
            'anchor': 'free',
            'side': 'left',
            'position': ax_pos
        })

    fig.update_layout(
        xaxis={
            'domain': [0.075 * (n_axes - 1), 1],
            'title': 'Date and time'
        },
        yaxis=layout_axes[0],
        yaxis2=layout_axes[1],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.show()
    return fig


def airflow_plot(df):
    df = df.rolling('300s').mean()
    fig = go.Figure()
    trace = go.Scattergl(
        x=df.index,
        y=df['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)'],
        name='Aeration',
        mode='lines',
        line=dict(
            dash='solid',
            color='red'
        ),
    )
    fig.add_trace(trace)
    fig.update_layout(
        xaxis={
            'title': 'Date and time'
        },
        yaxis={
            'title': 'Flow rate (L/h)',
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def threefigs(df):
    df.index = df.index.tz_convert('US/Eastern')
    '''fig = go.Figure(
        data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
        layout=go.Layout(
            title=go.layout.Title(text="A Bar Chart")
        )
    )'''
    # df = df.groupby(pd.Grouper(freq='300S')).first()
    fig = make_subplots(
        rows=3, cols=1,
        specs=[[{'secondary_y': True}], [{}], [{}]],
        shared_xaxes=True,
    )

    # Top
    # NH4
    trace_nh4 = go.Scatter(
        x=df.index,
        y=df['pilEAUte-Pilote effluent-Varion_002-NH4_N'] * 1000,
        name='Ammonia',
        mode='lines',
        line=dict(
            dash='solid',
            color='blue'
        ),
    )
    fig.add_trace(trace_nh4, row=1, col=1, secondary_y=False)

    # NO3
    trace_no3 = go.Scatter(
        x=df.index,
        y=df['pilEAUte-Pilote effluent-Varion_002-NO3_N'] * 1000,
        name='Nitrate',
        mode='lines',
        line=dict(
            dash='solid',
            color='turquoise'
        )
    )
    fig.add_trace(trace_no3, row=1, col=1, secondary_y=False)
    # AvN
    trace_avn = go.Scatter(
        x=df.index,
        y=df['pilEAUte-Pilote effluent-Varion_002-NH4_N']
        / df['pilEAUte-Pilote effluent-Varion_002-NO3_N'],
        name='AvN ratio',
        mode='lines+markers',
        line=dict(
            dash='solid',
            color='orange'
        ),
        marker={
            'opacity': 0
        }
    )
    fig.add_trace(trace_avn, row=1, col=1, secondary_y=True)

    # Middle
    df_mid = df.rolling('300s').mean()
    flow_trace = go.Scatter(
        x=df_mid.index,
        y=df_mid['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)'] * 1000 * 60,
        name='Aeration flow',
        mode='lines',
        line=dict(
            dash='solid',
            color='red'
        ),
    )
    fig.add_trace(flow_trace, row=2, col=1)
    fig.add_trace(flow_trace, row=3, col=1)
    # fig.update_layout(width=1200, height=800)
    fig.update_layout(legend_orientation="h")
    fig.update_layout(legend=dict(x=0, y=1.2))
    # fig.show(config={'displayModeBar': False})

    return fig
