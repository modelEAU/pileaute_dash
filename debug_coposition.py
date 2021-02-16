
    
    
#%%
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

    html.Div([
        html.Div([
            html.Div([
            html.H1('Influent Load [g/d]', style={'textAlign': 'center', 'color':'#7FDBFF'}),
            dcc.Graph(id='InfluentLoad')], className="four columns"),

            html.Div([
            html.H1('Influent concentration [mg/L]', style={'textAlign': 'center', 'color':'#7FDBFF'}),
            dcc.Graph(id='InfluentConcentration')], className="five columns"),

            html.Div([
            html.H1('Influent Parameter', style={'textAlign': 'center', 'color':'#7FDBFF'}),
            dcc.Graph(id='InfParmTable')], className="three columns"),
                ])
            ]),

        html.Br(),
        html.Div(
            children=[
                html.Div(
                    id='graph-div',
                    children=[
                        # html.H2(dcc.Markdown("Online data"), style={'textAlign': 'center'}),
                        #dcc.Graph(id='avn-graph',className='three columns'),
                        html.Div([ html.H1('oxygen level', style={'textAlign': 'center', 'color':'#7FDBFF'}), dcc.Graph(id='avn-graph')], className="six columns"),
                        html.Div([
                            html.H1('TSS concentration', style={'textAlign': 'center', 'color':'#7FDBFF'}),
                            dcc.Graph(id='Bio_perm')], className="six columns"),
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
                                        html.H2(
                                            'HRT',
                                            style={'textAlign': 'left'}
                                        ),
                                        dash_table.DataTable(
                                            id='SRT',
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
                                        html.H2(
                                            'SRT',
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
                                        html.Br(),
                                        html.Div(children=[html.H2('Aeration state',style={'textAlign': 'center', 'color': '#7FDBFF'}),dcc.Graph(id='Aeration_state')],) 
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
                    ],
                    style={
                        'float': 'right',
                        'width': '20%',
                        # 'borderStyle': "solid",
                        'display': 'inline-block',
                        'paddingLeft': '0%',
                        'paddingRight': '0%',
                    }
                ),
            ],
            style={'textAlign': 'center', 'paddingLeft': '0%', 'paddingRight': '0%', 'width': '100%'}
        ),

     html.Div(children=[html.H1('Effluent',style={'textAlign': 'center', 'color': '#7FDBFF'}),
        dcc.Graph(id='Effluent ')], 
         className="seven columns"),
])


app.run_server(debug=False)


#%%


app.run_server(debug=False)
#%%%

        # html.Div(
        #     children=[
        #         html.Div(
        #             id='graph-div',
        #             children=[
        #                 # html.H2(dcc.Markdown("Online data"), style={'textAlign': 'center'}),
        #                 dcc.Graph(id='avn-graph')
        #             ],
        #             style={
        #                 'float': 'left',
        #                 'width': '70%',
        #                 # 'borderStyle': 'solid',
        #                 'display': 'inline-block',
        #                 'paddingLeft': '2%',
        #                 'paddingRight': '0%',
        #             }
        #         ),
        #         html.Div(
        #             id='table-div',
        #             children=[
        #                 # html.H2(dcc.Markdown("Aggregate statistics"), style={'textAlign': 'center'}),
        #                 html.Div(
        #                     id='floor-1',
        #                     children=[
        #                         html.Div(
        #                             children=[
        #                                 html.H4(
        #                                     'Influent',
        #                                     style={'textAlign': 'left'}
        #                                 ),
        #                                 dash_table.DataTable(
        #                                     id='influent-table',
        #                                     columns=[{"name": i, "id": i} for i in ['Parameter', 'Now', 'Last 24 hrs']],
        #                                     style_as_list_view=True,
        #                                     style_header={
        #                                         'fontWeight': 'bold',
        #                                         'backgroundColor': 'rgb(230, 230, 230)',
        #                                     },
        #                                     style_cell_conditional=[
        #                                         {
        #                                             'if': {'column_id': c},
        #                                             'textAlign': 'left'
        #                                         } for c in ['Parameter']
        #                                     ],
        #                                     style_data_conditional=[
        #                                         {
        #                                             'if': {'row_index': 'odd'},
        #                                             'backgroundColor': 'rgb(248, 248, 248)'
        #                                         }
        #                                     ],
        #                                 ),
        #                             ],
        #                             style={
        #                                 'display': 'inline-block',
        #                                 'alignSelf': 'left',
        #                                 'width': '96%',
        #                                 'paddingLeft': '2%',
        #                                 'paddingRight': '2%'
        #                             },
        #                         ),
        #                         html.Br(),
        #                         html.Div(
        #                             children=[
        #                                 html.H4(
        #                                     'Effluent',
        #                                     style={'textAlign': 'left'},
        #                                 ),
        #                                 dash_table.DataTable(
        #                                     id='effluent-table',
        #                                     columns=[{"name": i, "id": i} for i in ['Parameter', 'Now', 'Last 24 hrs']],
        #                                     style_as_list_view=True,
        #                                     style_header={
        #                                         'fontWeight': 'bold',
        #                                         'backgroundColor': 'rgb(230, 230, 230)',
        #                                     },
        #                                     style_cell_conditional=[
        #                                         {
        #                                             'if': {'column_id': c},
        #                                             'textAlign': 'left'
        #                                         } for c in ['Parameter']
        #                                     ],
        #                                     style_data_conditional=[
        #                                         {
        #                                             'if': {'row_index': 'odd'},
        #                                             'backgroundColor': 'rgb(248, 248, 248)'
        #                                         }
        #                                     ],
        #                                 ),
        #                             ],
        #                             style={
        #                                 'display': 'inline-block',
        #                                 'alignSelf': 'left',
        #                                 'width': '96%',
        #                                 'paddingLeft': '2%',
        #                                 'paddingRight': '2%',
        #                             },
        #                         ),
        #                     ],
        #                 ),
        #                 html.Br(),
        #                 html.Div(
        #                     id='floor-2',
        #                     children=[
        #                         html.Div(
        #                             children=[
        #                                 html.H4(
        #                                     'Cumulative Stats',
        #                                     style={'textAlign': 'left'}
        #                                 ),
        #                                 dash_table.DataTable(
        #                                     id='bioreactor-table',
        #                                     columns=[{"name": i, "id": i} for i in ['Parameter', 'Last 24 hrs']],
        #                                     style_as_list_view=True,
        #                                     style_header={
        #                                         'fontWeight': 'bold',
        #                                         'backgroundColor': 'rgb(230, 230, 230)',
        #                                     },
        #                                     style_cell_conditional=[
        #                                         {
        #                                             'if': {'column_id': c},
        #                                             'textAlign': 'left'
        #                                         } for c in ['Parameter']
        #                                     ],
        #                                     style_data_conditional=[
        #                                         {
        #                                             'if': {'row_index': 'odd'},
        #                                             'backgroundColor': 'rgb(248, 248, 248)'
        #                                         }
        #                                     ],
        #                                 )
        #                             ],
        #                             style={
        #                                 'display': 'inline-block',
        #                                 'alignSelf': 'right',
        #                                 'width': '96%',
        #                                 'paddingLeft': '2%',
        #                                 'paddingRight': '2%'
        #                             },
        #                         ),
        #                     ],
        #                 ),
        #             ],
        #             style={
        #                 'float': 'right',
        #                 'width': '25%',
        #                 # 'borderStyle': "solid",
        #                 'display': 'inline-block',
        #                 'paddingLeft': '0%',
        #                 'paddingRight': '0%',
        #             }
        #         ),
        #     ],
        #     style={'textAlign': 'center', 'paddingLeft': '0%', 'paddingRight': '0%', 'width': '100%'}
        # ),
    html.Div(children=[
    html.H1('Effluent',style={'textAlign': 'center', 'color': '#7FDBFF'}),
      dcc.Graph(id='whichid',
             figure={
                 'data':[
                     {'x':[1,2,3,4,5], 'y':[2,6,4,1,0.8]}
                        ]}
             )],
            style={'display': 'inline-block',
                                        'alignSelf': 'left',
                                        'width': '96%',
                                        'paddingLeft': '2%',
                                        'paddingRight': '2%'
                                    } ),
    ]
)






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
    Output('avn-graph', 'figure'),
    [Input('avn-db-store', 'data')]
)
def avn_graph(data):
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        if len(df) == 0:
            raise PreventUpdate
        else:
            Qair_col = df["pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)"]
            print(Qair_col.mean())

            _, peak_average = calculateKPIs.peak_stats(Qair_col, 400 / (60 * 1000))
            #print("Peak average", peak_average)
            df.index = df.index.map(lambda x: x.tz_localize(None))
            # for col in df.columns:
            #    print(col, len(df[col].dropna()))
            if len(peak_average) != 0:
                df = pd.concat([df, peak_average], axis=1, sort=False)
                df["pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)-avg cycle"].interpolate(method='linear', inplace=True)
                df["pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)-fAE"].interpolate(method='linear', inplace=True)
            df = df[~df.isna()]
            print('trying to graph')
            print('After concat',len(df))
            # for col in df.columns:
                #print(col, len(df[col].dropna()))
            fig = PlottingTools.threefigs(df)
            print('finished creating the figure')
            # print('AvN fig has been created')
        return fig


@app.callback(
    Output('InfluentLoad', 'figure'),
    [Input('avn-db-store', 'data')])



def InfluentLoad(data):
    if not data:
        raise PreventUpdate
    else:
        df = pd.read_json(data)
        if len(df) == 0:
            raise PreventUpdate
        else:
            fig = PlottingTools.violinplotInfluent(df)
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
    Output('effluent-table', 'data'),
    [Input('refresh-interval', 'n_intervals')],
    [State('avn-db-store', 'data')])
def update_effluent_stats(refresh, data):
    if not data:
        raise PreventUpdate
    else:
        data = pd.read_json(data)
        if len(data) == 0:
            raise PreventUpdate
        else:  # effluent stats
            data.index = data.index.map(lambda x: x.tz_localize(None))
            NH4_col = data['pilEAUte-Pilote effluent-Varion_002-NH4_N'] * 1000
            NO3_col = data['pilEAUte-Pilote effluent-Varion_002-NO3_N'] * 1000
            NH4in_col = data['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N']
            NO3in_col = data['pilEAUte-Primary settling tank effluent-Spectro_010-NO3_N']
            NH4_now, NH4_24 = calculateKPIs.stats_24(NH4_col, OFFSET)

            NO3_now, NO3_24 = calculateKPIs.stats_24(NO3_col, OFFSET)

            NO2_now, NO2_24 = 0, 0

            AvN_now = NH4_now - (NO3_now + NO2_now)
            AvN_24 = NH4_24 - (NO3_24 + NO2_24)

            # influent values
            NH4in_now, NH4in_24 = calculateKPIs.stats_24(NH4in_col, OFFSET)
            NO3in_now, NO3in_24 = calculateKPIs.stats_24(NO3in_col, OFFSET)

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
        if len(data) == 0:
            raise PreventUpdate
        else:
            data.index = data.index.map(lambda x: x.tz_localize(None))
            air_col = data['pilEAUte-Pilote reactor 5-FIT_430-Flowrate (Gas)']  # m3/s
            pilwater_col = data['pilEAUte-Pilote influent-FIT_110-Flowrate (Liquid)']  # m3/s
            NH4eff_col = data['pilEAUte-Pilote effluent-Varion_002-NH4_N'] / 1000  # mg/l to kg/m3
            NO3eff_col = data['pilEAUte-Pilote effluent-Varion_002-NO3_N']  # kg/m3

            NH4in_col = data['pilEAUte-Primary settling tank effluent-Ammo_005-NH4_N'] / 1000  # mg/l to kg/m3
            NO3in_col = data['pilEAUte-Primary settling tank effluent-Spectro_010-NO3_N']  # kg/m3

            totNH4in = calculateKPIs.integrate_flow(NH4in_col, OFFSET)
            totNO3in = calculateKPIs.integrate_flow(NO3in_col, OFFSET)
            totNO2eff = 0
            totNH4eff = calculateKPIs.integrate_flow(NH4eff_col, OFFSET)
            totNO3eff = calculateKPIs.integrate_flow(NO3eff_col, OFFSET)
            tot_tin = (totNH4in + totNO3in) - (totNH4eff + totNO3eff + totNO2eff)
            tot_air = calculateKPIs.integrate_flow(air_col, OFFSET)
            tot_water = calculateKPIs.integrate_flow(pilwater_col, OFFSET)
            # print(f'Total air,(m3) {tot_air}')
            # print(f'Total water, (m3), {tot_water}')
            # print(f'Total TIN removed, kg, {tot_tin / 1000}')
            if tot_air != 0:
                tin_air = tot_tin / tot_air
            else:
                tin_air = 0

            if tot_water != 0:
                air_water = tot_air / tot_water
            else:
                air_water = 0

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

app.run_server(debug=False)
