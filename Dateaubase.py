# ## ATTENTION: This script only works on Windows with
# ## a VPN connection opened to the DatEAUbase Server
import pandas as pd
from collections import namedtuple
from sqlalchemy import create_engine
from urllib import parse
import time

# Setting constants
database_name = 'dateaubase2020'
local_server = r'GCI-PR-DATEAU02\DATEAUBASE'
remote_server = r'132.203.190.77\DATEAUBASE'

with open('login.txt') as f:
    username = f.readline().strip()
    password = f.readline().strip()


def connect_local(server, database):
    engine = create_engine(f'mssql://{local_server}/{database}?driver=SQL+Server?trusted_connection=yes', connect_args={'connect_timeout': 2}, fast_executemany=True)
    return engine


def connect_remote(server, database, login_file):
    with open(login_file) as f:
        username = f.readline().strip()
        password = parse.quote_plus(f.readline().strip())
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server', connect_args={'connect_timeout': 2}, fast_executemany=True)
    return engine

def get_last(db_engine):
    query = 'SELECT Value_ID, Timestamp FROM dbo.value WHERE Value_ID = (SELECT MAX(Value_ID) FROM dbo.value)'
    result = db_engine.execute(query)
    Record = namedtuple('record', result.keys())
    records = [Record(*r) for r in result.fetchall()]
    return records[0]

def engine_runs(engine):
    try:
        _ = get_last(engine)
    except Exception:
        return False
    else:
        return True

def date_to_epoch(date):
    naive_datetime = pd.to_datetime(date)
    local_datetime = naive_datetime.tz_localize(tz='US/Eastern')
    return int(local_datetime.value / 10**9)


def epoch_to_pandas_datetime(epoch):
    local_time = time.localtime(epoch)
    return pd.Timestamp(*local_time[:6])


def get_projects(connection):
    query = '''
SELECT DISTINCT Project_name
FROM project
ORDER BY Project_name ASC;'''
    df = pd.read_sql(query, connection)
    return df


def get_locations(connection, project):
    query = '''
SELECT dbo.sampling_points.Description
FROM sampling_points
left outer join dbo.project_has_sampling_points on dbo.project_has_sampling_points.Sampling_point_ID = dbo.sampling_points.Sampling_point_ID
left outer join dbo.project on dbo.project.Project_ID = dbo.project_has_sampling_points.Project_ID
WHERE
dbo.project.Project_name = \'{}\'
ORDER BY dbo.project.Project_ID ASC;
'''.format(project)
    locations = pd.read_sql(query, connection)
    return locations


def get_equipment(connection, project, location):
    query = '''
    SELECT dbo.equipment.Equipment_identifier
    FROM equipment
    left outer join dbo.equipment_has_sampling_points on dbo.equipment_has_sampling_points.Equipment_ID = dbo.equipment.Equipment_ID
    left outer join dbo.sampling_points on dbo.sampling_points.Sampling_point_ID = dbo.equipment_has_sampling_points.Sampling_point_ID
    left outer join dbo.project_has_sampling_points on dbo.project_has_sampling_points.Sampling_point_ID = dbo.sampling_points.Sampling_point_ID
    left outer join dbo.project on dbo.project.Project_ID = dbo.project_has_sampling_points.Project_ID
    WHERE
    dbo.project.Project_name = \'{}\'
    AND dbo.sampling_points.Sampling_location = \'{}\'
    ORDER BY dbo.project.Project_ID ASC;'''.format(project, location)
    equipment = pd.read_sql(query, connection)
    return equipment


def get_parameters(connection, project, location, equipment):
    query = '''
    SELECT dbo.parameter.Parameter
    FROM dbo.parameter
    left outer join dbo.equipment_model_has_parameter on dbo.equipment_model_has_parameter.Parameter_ID = dbo.parameter.Parameter_ID
    left outer join dbo.equipment_model on dbo.equipment_model.Equipment_model_ID = dbo.equipment_model_has_parameter.Equipment_model_ID
    left outer join dbo.equipment on dbo.equipment.Equipment_model_ID = dbo.equipment_model.Equipment_model_ID
    left outer join dbo.equipment_has_sampling_points on dbo.equipment_has_sampling_points.Equipment_ID = dbo.equipment.Equipment_ID
    left outer join dbo.sampling_points on dbo.sampling_points.Sampling_point_ID = dbo.equipment_has_sampling_points.Sampling_point_ID
    left outer join dbo.project_has_sampling_points on dbo.project_has_sampling_points.Sampling_point_ID = dbo.sampling_points.Sampling_point_ID
    left outer join dbo.project on dbo.project.Project_ID = dbo.project_has_sampling_points.Project_ID
    WHERE
    dbo.project.Project_name = \'{}\'
    AND dbo.sampling_points.Sampling_location = \'{}\'
    AND dbo.equipment.Equipment_identifier = \'{}\'
    ORDER BY dbo.project.Project_ID ASC;
    '''.format(project, location, equipment)
    parameters = pd.read_sql(query, connection)
    return parameters


def get_units(connection, project, location, equipment, parameter):
    query = '''
    SELECT dbo.unit.Unit
    FROM dbo.unit
    left outer join dbo.parameter on dbo.parameter.Unit_ID = dbo.unit.Unit_ID
    left outer join dbo.equipment_model_has_parameter on dbo.equipment_model_has_parameter.Parameter_ID = dbo.parameter.Parameter_ID
    left outer join dbo.equipment_model on dbo.equipment_model.Equipment_model_ID = dbo.equipment_model_has_parameter.Equipment_model_ID
    left outer join dbo.equipment on dbo.equipment.Equipment_model_ID = dbo.equipment_model.Equipment_model_ID
    left outer join dbo.equipment_has_sampling_points on dbo.equipment_has_sampling_points.Equipment_ID = dbo.equipment.Equipment_ID
    left outer join dbo.sampling_points on dbo.sampling_points.Sampling_point_ID = dbo.equipment_has_sampling_points.Sampling_point_ID
    left outer join dbo.project_has_sampling_points on dbo.project_has_sampling_points.Sampling_point_ID = dbo.sampling_points.Sampling_point_ID
    left outer join dbo.project on dbo.project.Project_ID = dbo.project_has_sampling_points.Project_ID
    WHERE
    dbo.project.Project_name = \'{}\'
    AND dbo.sampling_points.Sampling_location = \'{}\'
    AND dbo.equipment.Equipment_identifier = \'{}\'
    AND dbo.parameter.Parameter = \'{}\'
    ORDER BY dbo.project.Project_ID ASC;
    '''.format(project, location, equipment, parameter)
    units = pd.read_sql(query, connection)
    return units


def build_query(start, end, project, location, equipment, parameter):
    return '''SELECT dbo.value.Timestamp,
dbo.value.Value as measurement,
dbo.parameter.Parameter as par,
dbo.unit.Unit,
dbo.equipment.Equipment_identifier as equipment,
dbo.sampling_points.Sampling_location,
dbo.project.Project_name

FROM dbo.parameter
left outer join dbo.metadata on dbo.parameter.Parameter_ID = dbo.metadata.Parameter_ID
left outer join dbo.value on dbo.value.Metadata_ID = dbo.metadata.Metadata_ID
left outer join dbo.unit on dbo.parameter.Unit_ID = dbo.unit.Unit_ID
left outer join dbo.equipment on dbo.metadata.Equipment_ID = dbo.equipment.Equipment_ID
left outer join dbo.sampling_points on dbo.metadata.Sampling_point_ID = dbo.sampling_points.Sampling_point_ID
left outer join dbo.project on dbo.metadata.Project_ID = dbo.project.Project_ID
WHERE dbo.value.Timestamp > {}
AND dbo.value.Timestamp < {}
AND dbo.sampling_points.Sampling_location = \'{}\'
AND dbo.parameter.Parameter = \'{}\'
AND dbo.equipment.Equipment_identifier = \'{}\'
AND dbo.project.Project_name = \'{}\'
order by dbo.value.Value_ID;
'''.format(start, end, location, parameter, equipment, project)


def get_span(connection, project, location, equipment, parameter):
    query = '''SELECT  MIN(dbo.value.Timestamp), MAX(dbo.value.Timestamp)
    FROM dbo.parameter
    left outer join dbo.metadata on dbo.parameter.Parameter_ID = dbo.metadata.Parameter_ID
    left outer join dbo.value on dbo.value.Metadata_ID = dbo.metadata.Metadata_ID
    left outer join dbo.unit on dbo.parameter.Unit_ID = dbo.unit.Unit_ID
    left outer join dbo.equipment on dbo.metadata.Equipment_ID = dbo.equipment.Equipment_ID
    left outer join dbo.sampling_points on dbo.metadata.Sampling_point_ID = dbo.sampling_points.Sampling_point_ID
    left outer join dbo.project on dbo.metadata.Project_ID = dbo.project.Project_ID
    WHERE dbo.sampling_points.Sampling_location = \'{}\'
    AND dbo.parameter.Parameter = \'{}\'
    AND dbo.equipment.Equipment_identifier = \'{}\'
    AND dbo.project.Project_name = \'{}\';
    '''.format(location, parameter, equipment, project)

    df = pd.read_sql(query, connection)
    df.columns = ['first', 'last']
    first = epoch_to_pandas_datetime(df.at[0, 'first'])
    last = epoch_to_pandas_datetime(df.at[0, 'last'])
    return first, last


def clean_up_pulled_data(df, project, location, equipment, parameter):
    df['datetime'] = [epoch_to_pandas_datetime(x) for x in df.Timestamp]
    df.sort_values('datetime', axis=0, inplace=True)
    project = project.replace('-', '_')
    location = location.replace('-', '_')
    parameter = parameter.replace('-', '_')
    equipment = equipment.replace('-', '_')
    df.drop(
        ['Timestamp', 'Project_name', 'par', 'Unit', 'equipment', 'Sampling_location'],
        axis=1,
        inplace=True
    )
    df.rename(
        columns={
            'measurement': '{}-{}-{}-{}'.format(project, location, equipment, parameter),
        },
        inplace=True)
    df.set_index('datetime', inplace=True, drop=True)
    df = df[~df.index.duplicated(keep='first')]
    return df


def extract_data(connexion, extract_list):
    for i in range(len(extract_list)):
        query = build_query(
            extract_list[i]['Start'],
            extract_list[i]['End'],
            extract_list[i]['Project'],
            extract_list[i]['Location'],
            extract_list[i]['Equipment'],
            extract_list[i]['Parameter']
        )
        if i == 0:
            df = pd.read_sql(query, connexion)
            clean_up_pulled_data(
                df,
                extract_list[i]['Project'],
                extract_list[i]['Location'],
                extract_list[i]['Equipment'],
                extract_list[i]['Parameter']
            )
        else:
            temp_df = pd.read_sql(query, connexion)
            clean_up_pulled_data(
                temp_df,
                extract_list[i]['Project'],
                extract_list[i]['Location'],
                extract_list[i]['Equipment'],
                extract_list[i]['Parameter']
            )
            df = df.join(temp_df, how='outer')
            df = df[~df.index.duplicated(keep='first')]
    return df


def debug(engine):
    Start = date_to_epoch('2019-09-01 12:00:00')
    End = date_to_epoch('2019-10-01 12:00:00')
    Location = 'Primary settling tank effluent'
    Project = 'pilEAUte'

    param_list = ['COD','CODf','NH4-N','K']
    equip_list = ['Spectro_010','Spectro_010','Ammo_005','Ammo_005']

    extract_list={}
    for i in range(len(param_list)):
        extract_list[i] = {
            'Start':Start,
            'End':End,
            'Project':Project,
            'Location':Location,
            'Parameter':param_list[i],
            'Equipment':equip_list[i]
        }
    print('ready to extract')
    df = extract_data(engine, extract_list)
    print(len(df))

# ________Main Script_________
if __name__ == "__main__":
    engine = connect_local(local_server, database_name)
    if engine_runs(engine):
        print('Local connection engine is running')
    else:
        print('Local connection engine failed to connect --> Trying remote')
        engine = connect_remote(remote_server, database_name, 'login.txt')
        if engine_runs(engine):
            print('Remote connection engine is running')
            try:
                debug(engine)
            except Exception as e:
                print(e)
            finally:
                engine.dispose()
        else:
            print('Remote connection engine failed to connect. Quitting.')

