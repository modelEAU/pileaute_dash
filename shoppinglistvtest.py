

# EXTRACT DESIRED DATA
def AvN_shopping_list(beginning_string, ending_string):
    Project = 'pilEAUte'
    Location = [
        'Primary settling tank influent',
        'Pilote influent',
        'Copilote influent',
        'Primary settling tank effluent',
        'Primary settling tank effluent']
    equip_list = [
        'FIT-100',
        'FIT-110',
        'FIT-120', # flow
        'Ammo_005',
        'Ammo_005']
    param_list = [
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'Flowrate (Liquid)',
        'NH4-N',
        'K']
    shopping_list = {}
    for i in range(len(param_list)):
        shopping_list[i] = {
            'Start': Dateaubase.date_to_epoch(beginning_string),
            'End': Dateaubase.date_to_epoch(ending_string),
            'Project': Project,
            'Location': Location[i],
            'Parameter': param_list[i],
            'Equipment': equip_list[i]
        }
    return shopping_list



#querytest = 'SELECT dbo.value  FROM dbo.parameter WHERE [Sampling_location ]= 'Primary settling tank effluent' AND [dbo.parameter.Parameter] = 'NH4-N' AND dbo.equipment.Equipment_identifier = \'{}\'
#    AND dbo.project.Project_name = \'{}\';
#    '''.format(location, parameter, equipment, project)

#QueryTest=pd.read_sql(querytest, engine) 



Querysentense   =  build_query (Dateaubase.date_to_epoch('2020-03-20 16:56:52'),Dateaubase.date_to_epoch('2020-03-23 16:56:52'),  'pilEAUte', 'Primary settling tank effluent', 'Ammo_004','K')


Querytest= pd.read_sql(Querysentense, engine)

print(Querytest)



i= 0
query = build_query(
            Dateaubase.date_to_epoch('2020-01-23 16:56:52'),
            Dateaubase.date_to_epoch('2020-12-23 16:56:52'),
            'pilEAUte',
            'Pilote effluent',
            'Varion_002',
            'NO3-N'
        )


Querytest= pd.read_sql(query , engine)

print(Querytest)




i= 1
query = build_query(
            extract_list[i]['Start'],
            extract_list[i]['End'],
            extract_list[i]['Project'],
            extract_list[i]['Location'],
            extract_list[i]['Equipment'],
            extract_list[i]['Parameter']
        )


Querytest= pd.read_sql(query , engine)

print(Querytest)




i= 0
query = build_query(
            Dateaubase.date_to_epoch('2020-01-23 16:56:52'),
            Dateaubase.date_to_epoch('2020-12-23 16:56:52'),
            'pilEAUte',
            'Primary settling tank effluent',
            'Ammo_005',
            'K'
        )


Querytest= pd.read_sql(query , engine)

print(Querytest)





i= 0
query = build_query(
            Dateaubase.date_to_epoch('2020-01-23 16:56:52'),
            Dateaubase.date_to_epoch('2020-12-23 16:56:52'),
            'pilEAUte',
            'Primary settling tank effluent',
            'Spectro_010',
            'COD'
        )


Querytest= pd.read_sql(query , engine)

print(Querytest)





i= 0
query = build_query(
            Dateaubase.date_to_epoch('2020-01-23 16:56:52'),
            Dateaubase.date_to_epoch('2020-12-23 16:56:52'),
            'pilEAUte',
            'Primary settling tank effluent',
            'Spectro_010',
            'COD'
        )


Querytest= pd.read_sql(query , engine)

print(Querytest)




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
