import calculateKPIs
import pandas as pd
import Dateaubase

cursor, conn = Dateaubase.create_connection()
Start = Dateaubase.date_to_epoch('2020-02-23 00:00:00')
End = Dateaubase.date_to_epoch('2020-02-24 00:00:00')
Location = 'Pilote reactor 5'
Project = 'pilEAUte'

param_list = ['Flowrate (Gas)']
equip_list = ['FCV-430']

extract_list = {}
for i in range(len(param_list)):
    extract_list[i] = {
        'Start': Start,
        'End': End,
        'Project': Project,
        'Location': Location,
        'Parameter': param_list[i],
        'Equipment': equip_list[i]
    }

#Extract data
df = Dateaubase.extract_data(conn, extract_list)

#Define the column to be used
column = df['pilEAUte-Pilote reactor 5-FCV_430-Flowrate (Gas)']*60*1000;

#Calculate peak averages
peak_avg_overall, peak_avg, fAE = calculateKPIs.peak_stats(column, 0)
print(peak_avg.head())
print(fAE.head(500))

#Calculate stats
rate = True
min_value, max_value, avg_value, tot_value = calculateKPIs.stats(column, rate)
print(min_value, max_value, avg_value, tot_value)














