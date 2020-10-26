from itertools import cycle

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

COLORWAY = ['#f3cec9', '#e7a4b6', '#cd7eaf', '#a262a9', '#6f4d96', '#3d3b72', '#182844']

def debug():
    N = 1000
    t = np.linspace(0, 10, 100)
    y = np.sin(t)
    return go.Figure(data=go.Scatter(x=t, y=y, mode='lines'))


def debug_app(df):
    time = df.index
    traces = []
    for col in df.columns:
        trace = go.Scatter(
            x=time,
            y=df[col],
            mode='lines',
            line=dict(
                dash='solid',
            ),
            marker=dict(
                opacity=0,
            ),
            name=col.split('-')[-1],

        )
        traces.append(trace)
    fig = go.Figure(data=traces)
    fig.update_traces(connectgaps=True)
    return fig


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
    #df.index = df.index.tz_convert('US/Eastern')
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
    time = df.index
    '''df.sort_index(inplace=True)
    df.fillna(inplace=True, method='ffill')
    df = df.groupby(pd.Grouper(freq='300S')).first()'''
    fig = make_subplots(
        rows=3, cols=1,
        specs=[[{'secondary_y': True}], [{}], [{'secondary_y': True}]],
        shared_xaxes=True,
    )

    # Top
    # NH4
    trace_nh4 = go.Scattergl(
        x=time,
        y=df['pilEAUte-Pilote effluent-Varion_002-NH4_N'] * 1000,
        name='NH4',
        mode='lines',
        line=dict(
            dash='solid',
            color='firebrick'
        ),
    )
    fig.add_trace(trace_nh4, row=1, col=1, secondary_y=False)

    # NO3
    trace_no3 = go.Scattergl(
        x=time,
        y=df['pilEAUte-Pilote effluent-Varion_002-NO3_N'] * 1000,
        name='NO3',
        mode='lines',
        line=dict(
            dash='solid',
            color='seagreen'
        )
    )
    fig.add_trace(trace_no3, row=1, col=1, secondary_y=False)
    # AvN
    trace_avn = go.Scatter(
        x=time,
        y=df['pilEAUte-Pilote effluent-Varion_002-NH4_N']* 1000 - df['pilEAUte-Pilote effluent-Varion_002-NO3_N']* 1000,
        name='AvN difference',
        mode='lines+markers',
        line=dict(
            dash='solid',
            color='royalblue'
        ),
        marker={
            'opacity': 0
        }
    )
    fig.add_trace(trace_avn, row=1, col=1, secondary_y=True)

    trace_avn_sp = go.Scatter(
        x=df.index,
        y=[0]*len(df.index),
        name = 'AvN setpoint',
        mode='lines',
        legendgroup='leg3',
        line=dict(
            color='dimgrey',
            dash="dash",
        ),
        marker={
            'opacity': 0
        }
    )
    fig.add_trace(trace_avn_sp, row=1, col=1, secondary_y=True)

    # Middle
    df_mid = df.rolling('300s').mean()

    flow_trace = go.Scatter(
        x=df_mid.index,
        y=df_mid['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)'] * 1000 * 60,
        name='Airflow rate',
        mode='lines',
        line=dict(
            dash='solid',
            color='goldenrod',
            shape='hv'
        ),
    )
    fig.add_trace(flow_trace, row=2, col=1)

    # Average cycle
    if 'pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)-avg cycle' in df.columns:
        avg_cycle_trace = go.Scatter(
            x=time,
            y=df['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)-avg cycle'] * 1000 * 60,
            name='Average cycle',
            mode='lines',
            line=dict(
                dash='solid',
                color='blueviolet',
                shape='hvh'  # 'hvh'
            ),
        )
        fig.add_trace(avg_cycle_trace, row=3, col=1, secondary_y=False)

    if 'pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)-fAE' in df.columns:
        avg_cycle_trace = go.Scatter(
            x=time,
            y=df['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)-fAE']*100,
            name='Aerobic fraction',
            mode='lines',
            line=dict(
                dash='solid',
                color='darksalmon',
                shape='hvh'  # 'hvh'
            ),
        )

        fig.add_trace(avg_cycle_trace, row=3, col=1, secondary_y=True)


    # Subplot specific layouts
    fig.update_yaxes(title_text="[mg/L]", title_font=dict(size=14),range=[0, 20], row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="[-]", title_font=dict(size=14),range=[-10, 10], row=1, col=1, secondary_y=True)
    fig.update_yaxes(title_text="[L/min]", title_font=dict(size=14),range=[-50, 1000], row=2, col=1)
    fig.update_yaxes(title_text="[L/min]", title_font=dict(size=14),range=[500, 1000], row=3, col=1,  secondary_y=False)
    fig.update_yaxes(title_text="[-]", title_font=dict(size=14), range=[0, 100], row=3, col=1,  secondary_y=True)

    # General figure layout
    showgrid=True
    gridcolor = 'rgb(204, 204, 204)'
    gridwidth=1

    showline=True
    linecolor='rgb(153, 153, 153)'
    linewidth=2

    fig.update_xaxes(
        showgrid=showgrid,
        gridwidth=gridwidth,
        gridcolor=gridcolor,
        showline=showline,
        linewidth=linewidth,
        linecolor=linecolor,
    )
    fig.update_yaxes(
        showgrid=showgrid,
        gridwidth=gridwidth,
        gridcolor=gridcolor,
        showline=showline,
        linewidth=linewidth,
        linecolor=linecolor,
    )

    fig.update_layout(height=800)
    fig.update_layout(legend_orientation="h")
    fig.update_layout(legend=dict(x=0, y=1.1))
    #fig.show(config={'displayModeBar': False})
    fig.update_traces(connectgaps=True)
    return fig




def violinplotInfluent(df,offset):
    import math
    df.index = df.index.map(lambda x: x.tz_localize(None))
    threshold_time = pd.to_datetime(datetime.now() - timedelta(weeks=offset) - timedelta(hours=24*7))
    df = df[df.index > threshold_time]
    df.sort_index(inplace=True)
    df.fillna(inplace=True, method='ffill')
    df = df.groupby(pd.Grouper(freq='300S')).first()
    #Spectro unit is 1000 times
    SpectroColum=[df.columns[df.columns.str.contains('Spectro')]]
    df[SpectroColum[0]]=df[SpectroColum[0]]*1000
    InfluentVariabletotal = [col for col in df.columns if 'pilEAUte-Primary settling tank effluent' in col]
    InfluentVariabletotal = pd.DataFrame(InfluentVariabletotal) 
    
    InfluentVariable=InfluentVariabletotal[ ~ InfluentVariabletotal[0].str.contains('Temperature')]
    InfluentVariable=InfluentVariable[ ~ InfluentVariable[0].str.contains('pH')]
    InfluentVariable=InfluentVariable[ ~ InfluentVariable[0].str.contains('NO3')]

    InfluentVariable=InfluentVariable[0].tolist()
    Flow=df['pilEAUte-Primary settling tank influent-FIT_100-Flowrate (Liquid)']*1000
    closnumber=math.ceil(len(InfluentVariable)/2)
    fig = make_subplots(rows=2, cols=closnumber)
    # Top
    for i, element in enumerate(InfluentVariable):
        print(i, str(element))
        Load=df[str(element)].mul(Flow)*24 # (mg/l*m3/h->g/d)
        plotname=go.Violin(y=Load,box_visible=True, meanline_visible=True, name=element[40:])
        if i + 1 <= closnumber:
            fig.add_trace(plotname,row=1,col=i+1)
        else:
            fig.add_trace(plotname,row=2,col=i-closnumber+1)
    # fig.update_layout(legend=dict(
    # orientation="h",
    # yanchor="bottom",
    # y=1.02,
    # xanchor="right",
    # x=1))
    return fig




def InfluentConcen(df,offset):
    df.sort_index(inplace=True)
    df.fillna(inplace=True, method='ffill')
    df.index = df.index.map(lambda x: x.tz_localize(None))
    df = df.groupby(pd.Grouper(freq='300S')).first()
    threshold_time = pd.to_datetime(datetime.now() - timedelta(weeks=offset) - timedelta(hours=24*7))
    df = df[df.index > threshold_time]
    time = df.index

    SpectroColum=[df.columns[df.columns.str.contains('Spectro')]]
    df[SpectroColum[0]]=df[SpectroColum[0]]*1000

    fig = make_subplots(
        rows=3, cols=1,
        specs=[[{'secondary_y': True}], [{'secondary_y': True}], [{'secondary_y': True}]],
        shared_xaxes=True,)

    # Top
    # NH4
    trace_nh4 = go.Scattergl(
        x=time,
        y=df['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N'],
        name='K',
        mode='lines',
        line=dict(
            dash='solid',
            color='blue'))

    trace_K = go.Scattergl(
        x=time,
        y=df['pilEAUte-Primary settling tank effluent-Ammo_005-K'],
        name='NH4',
        mode='lines',
        line=dict(
            dash='solid',
            color='violet'))


    trace_rain = go.Bar(x=time,y=df['Rain'],name='Rain')
    fig.add_trace(trace_nh4, row=1, col=1, secondary_y=False),
    fig.add_trace(trace_K, row=1, col=1, secondary_y=True),
    fig.add_trace(trace_rain, row=1, col=1, secondary_y=True),



    trace_COD = go.Scattergl(
    x=time,
    y=df['pilEAUte-Primary settling tank effluent-Spectro_010-COD'],
    name='COD',
    mode='lines',
    line=dict(
        dash='solid',
        color='lightcoral'))

    trace_CODf = go.Scattergl(
    x=time,
    y=df['pilEAUte-Primary settling tank effluent-Spectro_010-CODf'],
    name='COD_f',
    mode='lines',
    line=dict(
        dash='solid',
        color='darkorange'))
    fig.add_trace(trace_COD, row=2, col=1, secondary_y=False)

    trace_TSS = go.Scattergl(
    x=time,
    y=df['pilEAUte-Primary settling tank effluent-Spectro_010-TSS'],
    name='TSS',
    mode='lines',
    line=dict(
        dash='solid',
        color='dimgrey'))
    fig.add_trace(trace_COD, row=2, col=1, secondary_y=False)
    fig.add_trace(trace_CODf, row=2, col=1, secondary_y=False),
    fig.add_trace(trace_TSS, row=2, col=1, secondary_y=True),


    ratioCOD_NH4=df['pilEAUte-Primary settling tank effluent-Spectro_010-COD']/ df['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N']
    trace_ratioCOD_NH4 = go.Scattergl(x=time, y =ratioCOD_NH4,
        name='COD/NH4 ratio, typical COD/TN~8-12',
        line=dict(
        dash='longdashdot',
        color='dimgrey'))

    ratioCOD_TSS=df['pilEAUte-Primary settling tank effluent-Spectro_010-COD']/ df['pilEAUte-Primary settling tank effluent-Spectro_010-TSS']
    trace_ratioCOD_TSS = go.Scattergl(x=time, y =ratioCOD_TSS,
        name='COD/TSS ratio, typical COD/VSS~1.4~1.6',
        line=dict(
        dash='longdashdot',
        color='saddlebrown'))

    
    fig.add_trace(trace_ratioCOD_NH4, row=3, col=1, secondary_y= False)
    
    fig.add_trace(trace_ratioCOD_TSS, row=3, col=1, secondary_y= True)
    return fig




#***********Oxygen Level************

def oxylevelplot(df,offset):
    df.sort_index(inplace=True)
    df.fillna(inplace=True, method='ffill')
    df.index = df.index.map(lambda x: x.tz_localize(None))
    df = df.groupby(pd.Grouper(freq='300S')).first()
    threshold_time = pd.to_datetime(datetime.now() - timedelta(weeks=offset) - timedelta(hours=24*7))
    df = df[df.index > threshold_time]
    time = df.index


    fig = make_subplots(rows=2, cols=2, row_heights=[0.7, 0.3], specs=[ 
         [{'colspan': 2, 'type':'xy'}, None],
        [{ 'colspan': 2}, None] 
           ])
#Here is an example that creates a 2 by 2 subplot grid containing 3 subplots. The subplot specs element for position (1, 1) has a colspan value of 2, causing it to span the full figure width. The subplot specs element for position (1, 2) is None because no subplot begins at this location in the grid.


    trace_pileauteOxyg = go.Scattergl(
        x=time,
        y=df['pilEAUte-Pilote reactor 4-AIT_241-DO'],
        name='DO-pileaute',
        mode='lines',
        line=dict(
            dash='solid',
            color='dodgerblue'))

    trace_copOxyg = go.Scattergl(
    x=time,
    y=df['pilEAUte-copilote reactor 5-AIT_341-DO'],
    name='DO-Copileaute',
    mode='lines',
    line=dict(
        dash='solid',
        color='olive'))

    fig.add_trace(trace_pileauteOxyg, row=1, col=1, secondary_y= False)
    fig.add_trace(trace_copOxyg, row=1, col=1, secondary_y= False)




    AirvalueNow=df['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)'][-1]
    AirvalueNowcop=df['pilEAUte-copilote reactor 5-FIT_460-Flowrate (Gas)'][-1]
    Maxvalue=(df[['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)','pilEAUte-copilote reactor 5-FIT_460-Flowrate (Gas)']].max()).max()
    # Airpileaute=go.Scatterpolar(r=[1,2,3,4,5], theta = [1,2,3,4,5], name ='Airpileaute',mode = "lines+markers",marker = dict(
    #         color = "royalblue",
    #         symbol = "star-triangle-down",
    #         size = 8) )
    Airpileaute=go.Scattergl(x= [AirvalueNow,AirvalueNow], y= [0 , 1], mode = "lines+markers", line=dict(width=5), name='airflow pileaute reactor5', marker = dict(
            color = "burlywood", line = dict(width=1), 
            symbol = "star-triangle-up",
            size = 10))
    Aircopileaute=go.Scattergl(x= [AirvalueNowcop,AirvalueNowcop], y= [0 , 1], name='airflow copileaute reactor5',  mode = "lines+markers", line=dict(width=5), marker = dict(color = "black", line = dict(width=1), symbol = "star-triangle-up",size = 10))
    Bardivn=100
    fig.add_trace(go.Bar(x=np.arange(0.0001, 3* Maxvalue, 3* Maxvalue/Bardivn), y=np.linspace(1,1,Bardivn), name='Air dashboard', marker=dict(color=np.arange(0.0001, 4*Maxvalue,3*Maxvalue/Bardivn), colorscale='bluered'), width=0.02), row= 2, col=1)
    fig.add_trace(Airpileaute, row= 2, col=1 )
    fig.add_trace(Aircopileaute, row= 2, col=1 )
    annotations = []
    annotations.append(dict(xref='x2', yref='y2', x=AirvalueNow, y=0.7,  text= str(round(AirvalueNow,3)) ,font=dict(family='Arial', size=20, color='black'),showarrow=False))
    annotations.append(dict(xref='x2', yref='y2', x=AirvalueNowcop, y=0.3, text= str(round(AirvalueNowcop,3)) ,font=dict(family='Arial', size=20,color='black'),showarrow=False))

    fig.update_layout(annotations=annotations)
    return fig
#   
#x=[np.arange(0,1,0.1)], y=np.linspace(1,1,10)  ,np.linspace(1,1,10) , 








if __name__ == '__main__':
    start = time.time()
    fig = debug()
    fig.show()
    end = time.time()
    print(f'This took {end-start} seconds')

