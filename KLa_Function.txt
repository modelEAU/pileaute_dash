def calc_kla(df, Start, End, Sample_Volume, Cal_Volume):  # Volumes in liters
    # Make a copy of the DataFrame to work on #####
    DF = df[Start:End].copy(deep=True)

    # Add the new columns we need to the DataFrame #####
    NewColumns = [
        'Co', 'Ce', 'Kla', 'Area', 'stBOD', 'OURex', 'PeakNo', 'ReacVol',
        'DO_Start', 'DO_End', 'DO_Bend', 'DO_Bottom', 'x_plot', 'y_plot',
    ]
    for name in NewColumns:
        if name not in DF.columns:
            DF.insert(len(DF.columns), name, np.nan)

    # Find important points in peaks (Start, End, Bend, Bottom) #####
    # Filter the DataFrame to find the starting point of a respirogram
    Percentile = np.percentile(DF['DO_A'], 70)
    # Filtered= DF.loc[(DF.index==DF.first_valid_index()) | ((DF['DO_A'] > Percentile) & (DF['DOdt_A'].diff(-1) > 0) & (DF['DOdt_A'] > 0) & (DF['DOdt_A'].shift(-1) < 0)& (DF['DO_A']>DF['DO_A'].shift(-1)))]
    Filtered = DF.loc[(DF.index == DF.first_valid_index()) | ((DF['DO_A'] > Percentile) & (DF['DOdt_A'] > 0) & (DF['DOdt_A'].shift(-1) < 0))]

    Filtered['Start'] = pd.to_datetime(Filtered.index)
    Filtered['DO_Start'] = Filtered['DO_A']
    # remove false positives by removing the Start points that are too close together in time
    i = 0
    while i < len(Filtered) - 1:
        duration = pd.to_timedelta(Filtered['Start'].iloc[i + 1] - Filtered['Start'].iloc[i]).total_seconds()
        if duration <= pd.to_timedelta('5 minutes').total_seconds():
            Filtered = Filtered.drop(Filtered.index[i])
            i = 0
        else:
            i += 1
    # Add columns to the filtered DataFrame for the other key points in the respirogram
    Filtered = Filtered.reset_index(drop=True)

    Columns = ['End', 'Bend', 'Bottom']
    for name in Columns:
        Filtered.insert(len(Filtered.columns), name, np.nan)
    for i in range(len(Filtered) - 1):
        # Defining the end of each respirogram
        Filtered['End'].iloc[i] = Filtered['Start'].iloc[i + 1]
        Filtered['DO_End'].iloc[i] = DF['DO_A'][Filtered['End'].iloc[i]]

        S = Filtered['Start'].iloc[i]
        E = Filtered['End'].iloc[i]
        # Find the lowest point of each respirogram
        BottomDO = DF[S:E]['DO_A'].min()
        Bottom_pos = pd.to_datetime(DF[S:E].loc[DF[S:E]['DO_A'] == DF[S:E]['DO_A'].min()].index)

        Filtered['Bottom'].iloc[i] = Bottom_pos[0]
        Filtered['DO_Bottom'].iloc[i] = BottomDO
        # Finding the "Bend" in each respirogram - the point at which biodegradation is complete
        # The Bend corresponds to the last peak of the derivative over the span of the respirogram
        bendS = Filtered['Bottom'].iloc[i]
        bendE = Filtered['End'].iloc[i]
        benddf = DF[bendS:bendE].copy(deep=True)
        benddf.reset_index(inplace=True)
        n = 51
        dist = int((n - 1) / 2)
        x = benddf['Time'].iloc[dist:-dist]
        if len(benddf) <= 1.5 * n:
            Filtered['Bend'].iloc[i] = bendS
            Filtered['DO_Bend'].iloc[i] = np.nan
        else:
            RolledDO = rolling_window(benddf['DOdt_A'], n)
            RolledMax = np.max(RolledDO, axis=1)

            Compa = pd.DataFrame(
                {'DOdt': benddf['DOdt_A'].iloc[dist:-dist],
                    'Max': RolledMax,
                    'Time': x}
            )

            Compa = Compa.loc[Compa['DOdt'] == Compa['Max']]

            Compa.reset_index(inplace=True, drop=True)
            if len(Compa) == 0:
                Filtered['Bend'].iloc[i] = bendS
                Filtered['DO_Bend'].iloc[i] = np.nan
            else:
                LastMax = Compa.iloc[Compa.last_valid_index()]
                Filtered['Bend'].iloc[i] = LastMax['Time']
                Filtered['DO_Bend'].iloc[i] = DF['DO_A'].loc[Filtered['Bend'].iloc[i]]

        # If the interval between two respirograms is too large, the End of the first respirogram is set (arbitrarily) to 15 minutes after the end of biodegradation.
        if pd.to_timedelta(Filtered['End'].iloc[i] - Filtered['Start'].iloc[i]) > pd.to_timedelta('2 hours'):
            Set = pd.to_datetime(Filtered['Bend'].iloc[i]) + pd.to_timedelta('15 minutes')
            Filtered['End'].iloc[i] = pd.to_datetime(DF.iloc[[DF.index.get_loc(Set, method='nearest')]].index)[0]
            Filtered['DO_End'].iloc[i] = DF['DO_A'][Filtered['End'].iloc[i]]

    S = DF.first_valid_index()
    E = Filtered['Bottom'].iloc[0]

    TopDO = DF[S:E]['DO_A'].max()
    Top_pos = pd.to_datetime(DF[S:E].loc[DF[S:E]['DO_A'] == TopDO].index)
    Filtered['Start'].iloc[0] = Top_pos[0]
    Filtered['DO_Start'].iloc[0] = TopDO
    # Drops the last row of the filtered DataFrame, which only contains a Start point with no corresponding End, Bottom or Bend
    Filtered = Filtered[:-1]

    # Assign the Important points to the appropriate rows in the original DataFrame
    for i in range(len(Filtered)):
        DF['DO_Start'][Filtered['Start'][i]] = Filtered['DO_Start'][i]
        DF['DO_End'][Filtered['End'][i]] = Filtered['DO_End'][i]
        DF['DO_Bend'][Filtered['Bend'][i]] = Filtered['DO_Bend'][i]
        DF['DO_Bottom'][Filtered['Bottom'][i]] = Filtered['DO_Bottom'][i]

    # Plotting the Important points ######
    Label1 = ['DO']
    Label2 = ['Start', 'End', 'Bend', 'Bottom']
    Units1 = ['mg/l']
    Units2 = ['mg/l', 'mg/l', 'mg/l', 'mg/l']
    marks = ['lines', 'markers']
    start_plot = DF.first_valid_index()
    end_plot = DF.last_valid_index()
    figure = Plotit(DF, start_plot, end_plot, ['DO_A'], ['DO_Start', 'DO_End', 'DO_Bend', 'DO_Bottom'], Label1, Label2, Units1, Units2, marks)
    py.offline.iplot(figure)
    # Kla estimation ####

    # Define the re-aeration function under conditions without biodegradation

    def f(t, Kla, Ce, Co):
        return Ce - (Ce - Co) * np.exp(-Kla * (t))

    # Add relevant columns to the Filtered DataFrame
    Kla_columns = ['Co', 'Ce', 'Kla', 'std_err']
    for name in Kla_columns:
        if name not in Filtered.columns:
            Filtered.insert(len(Filtered.columns), name, np.nan)

    for i in range(len(Filtered)):
        if ((Filtered['Bend'].iloc[i] == Filtered['End'].iloc[i]) | (pd.to_timedelta(Filtered['End'].iloc[i] - Filtered['Bend'].iloc[i]).total_seconds() <= pd.to_timedelta('8 minutes').total_seconds())):
            print('Peak {} of {} is skipped: Interval too short.'.format(i + 1, len(Filtered)))
            continue
        else:
            # Define a DataFrame containing only the re-aeration phase of respirogram i
            T00 = Filtered['Bend'][i]
            Tf = Filtered['End'][i]
            print('Peak {} of {}. Start is at {}'.format(i + 1, len(Filtered), T00))

            Timedel = pd.to_timedelta(Tf - T00)
            rollingdf = DF[T00: T00 + 0.9 * Timedel]
            rollingdf['tvalue'] = rollingdf.index

            # Create a DataFrame to contain the results of non-linear regressions operated on sub-sections of the re-aeration phase
            SubResult = pd.DataFrame(index=range(0, int(0.5 * len(rollingdf))), columns=['Start', 'End', 'Ce', 'Co', 'Kla', 'std_err'])

            # Try to perform a non-linear regression on several sub-section of the re-aeration phases
            for j in range(len(rollingdf)):
                # The beginning of the range of the non-linear regression shifts one data point forward at each iteration
                # The final value in the range stays constant
                T0 = rollingdf['tvalue'].iloc[[j]][0]
                y_given = DF['DO_A'][T0:Tf].copy()
                y_frame = y_given.to_frame()
                y_frame.reset_index(drop=True, inplace=True)
                x_given = (DF[T0:Tf].index - T0).total_seconds()

                try:
                    # Define the bounds of the non-linear regression for parameters Kla, Ce, Co
                    param_bounds = ([0, 0, -20], [100 / 3600, 20, 20])
                    # Try to perform the non-linear regression
                    params, cov = scipy.optimize.curve_fit(f, x_given, y_frame['DO_A'], bounds=param_bounds)
                # Move on to the next sub-section if the non-linear regression fails
                except RuntimeError:
                    continue
                # If it doesn't fail, assign the results of the non-linear regression to the SubResult DataFrame
                else:
                    SubResult['Start'][j] = pd.to_datetime(T0)
                    SubResult['End'][j] = pd.to_datetime(Tf)
                    SubResult['Ce'][j] = params[1]
                    SubResult['Co'][j] = params[2]
                    SubResult['Kla'][j] = params[0]
                    perr = np.sqrt(np.diag(cov))
                    sterr = perr[0]
                    SubResult['std_err'][j] = sterr
                # And delete stored variables which are no longer needed
                finally:
                    del y_given
                    del y_frame
                    del x_given
            # If the non-linear regressions have succeeded at leat once over all the sub-sections of the re-aeration phase:
            if len(SubResult) != 0:
                # Select the values of Ce, Co and Kla for the iteration with the lowest standard error
                ''' TopDO = DF[S:E]['DO_A'].max()
                    Top_pos = pd.to_datetime(DF[S:E].loc[DF[S:E]['DO_A']== TopDO].index)
                    Filtered['Start'].iloc[0] = Top_pos[0]
                    Filtered['DO_Start'].iloc[0] = TopDO'''
                SubResult['std_err'] = SubResult['std_err']**2
                Min_err = SubResult['std_err'].min()
                index_position = SubResult.loc[SubResult['std_err'] == Min_err].index
                Filtered['Ce'][i] = SubResult['Ce'][index_position]
                Filtered['Co'][i] = SubResult['Co'][index_position]
                Filtered['Kla'][i] = SubResult['Kla'][index_position] * 3600
                Filtered['std_err'][i] = SubResult['std_err'][index_position]
                # Calculate the corresponding DO saturation concentration
            # If all non-linear regressions failed, move on to the next respirogram without assigning values
            else:
                continue
    # Fill the Filtered DataFrame with values from the nearest successful non-linear regression
    Columns = ['Ce', 'Co', 'Kla', 'std_err']
    for name in Columns:
        Filtered[name] = Filtered[name].fillna(method='ffill')
    # Assign the obtained Kla, Ce, Co and Cs values to the original DataFrame
    Columns = ['Kla', 'Ce', 'Co']
    for name in Columns:
        for i in range(len(Filtered)):
            DF[name][Filtered['Start'][i]:Filtered['End'][i]] = Filtered[name][i]

    # Re-calculate the expected DO concentrations during re-aeration using the found Kla, Ce and Co values and plot them
    def f2(t, Ce, Co, Kla, to):
        return Ce - (Ce - Co) * np.exp(-Kla * pd.to_timedelta(t - to).astype('timedelta64[s]'))

    DF['x_plot'] = pd.to_datetime(DF.index)
    for i in range(len(Filtered)):
        DF['y_plot'].loc[Filtered['Bend'][i]:Filtered['End'][i]] = f2(DF['x_plot'], DF['Ce'], DF['Co'], DF['Kla'] / 3600, Filtered['Bend'][i])

    Label1 = ['DO exp.', 'DO calc.', 'Ce']
    Label2 = ['KLa']
    Units1 = ['mg/l', 'mg/l', 'mg/l']
    Units2 = ['h-1']
    marks = ['lines', 'lines']
    start_plot = DF.first_valid_index()
    end_plot = DF.last_valid_index()
    figure = Plotit(DF, start_plot, end_plot, ['DO_A', 'y_plot', 'Ce'], ['Kla'], Label1, Label2, Units1, Units2, marks)
    py.offline.iplot(figure)
    return DF, Filtered
