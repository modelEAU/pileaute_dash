# ## ATTENTION: This script only works on Windows with
# ## a VPN connection opened to the DatEAUbase Server
import pandas as pd
import pyodbc


def create_connection():
    #with open('login.txt') as f:
    #    usr = f.readline().strip()
    #    pwd = f.readline().strip()
    # username = usr  # input("Enter username")
    # password = pwd  # getpass.getpass(prompt="Enter password")
    '''config = dict(
        server='10.10.10.10',  # change this to your SQL Server hostname or IP address
        port=1433,  # change this to your SQL Server port number [1433 is the default]
        database='dateaubase2020',
        username=username,
        password=password)'''
    conn_str = (
        r'Driver={SQL Server};'
        r'Server=localhost;' #{server},{port};'
        r'Database=dateaubase2020;'  #{database};'
        r'Trusted_Connection=yes;'  #'UID=jeandavidt;'
        )
    print(conn_str)
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    return cursor, conn


def date_to_epoch(date):
    datetime = pd.to_datetime(date)
    return int(datetime.value / 10**9)


def epoch_to_pandas_datetime(epoch):
    timestamp = pd.to_datetime(epoch * 10 ** 9)
    return timestamp


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


'''cursor, conn = create_connection()

Start = date_to_epoch('2020-02-24 17:00:00')
End = date_to_epoch('2020-02-26 17:00:00')
Location = 'Pilote reactor 4'
Project = 'pilEAUte'

param_list = ['Flowrate (Gas)']
equip_list = ['FIT-420']

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
print('ready to extract')
df = extract_data(conn, extract_list)


unit = get_units(conn, 'pilEAUte', 'Pilote reactor 4', 'FIT-420', 'Flowrate (Gas)y')
print(df)'''
