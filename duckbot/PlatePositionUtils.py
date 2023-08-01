
import os
import json
import pandas as pd
n = 0
while n != 5:
    curr_folder = os.path.basename(os.path.normpath(os.getcwd()))
    if curr_folder == 'duckbot':
        break
    os.chdir('..')
    n = n + 1
    
import ConfigFiles.PlatePositionsConfig as ppc




# ----------
#FETCHING WELL COORDINATES

def assign_plates_and_wells(master_expt_list):
    plates = [1,2,3,4,5]
    rows = ["A","B","C","D"]
    columns = ["1","2","3","4","5","6",]

    platewell_id_list =[]
    p_index = 0
    r_index = 0
    c_index = 0
    for x in range(len(plates)*len(rows)*len(columns)):
        platewell_id_list.append("Plate_"+ str(plates[p_index])+"_Well_"+str(rows[r_index])+str(columns[c_index]))
        c_index = c_index+1
        if c_index == 6: 
            c_index = 0 
            r_index = r_index + 1
        if r_index == 4:
            r_index = 0
            p_index = p_index + 1
            
    for i,x in enumerate(master_expt_list):
        x["plate_well_id"] = platewell_id_list[i]
    
    
    for s in master_expt_list:
        s['Plate'] = s["plate_well_id"][0:7]
        s['Well'] = s["plate_well_id"][13:16]
        
    return(master_expt_list)


# Method to return an updated version of the wells_in_plate dictionary defined above
# with 'x' and 'y' values added into each well dictionary, calculated for the specific plate. 

def fetch_plate_wellpostions(plate_num):
    plate_of_interest = next(p for p in ppc.plates if p["plate_id"] == plate_num)
    start_x = ppc.plate_start_position["x"] + (plate_of_interest["col"] * ppc.plate_column_offset)
    start_y = ppc.plate_start_position["y"] - (plate_of_interest["row"] * ppc.plate_row_offset)
    wells_in_plate = ppc.wells_in_plate
    for i, well in enumerate(wells_in_plate):
        well["x"] = start_x + (well["col"] * ppc.well_column_offset)
        well["y"] = start_y - (well["row"] * ppc.well_row_offset)
    return(wells_in_plate)


def add_well_coords_to_df_from_file(expt_setup_dir, expt_setup_filename):
    os.chdir(expt_setup_dir)
    with open(expt_setup_filename) as datafile:
        expt_data = json.load(datafile)
    sample_data = expt_data["sample_info"]
    df = pd.DataFrame(sample_data)
    unique_plates = list(df.Plate.unique())
    def pull_last_number(n):
        return n[-1:]
    plates_to_process = list(map(pull_last_number, unique_plates))
    for pl in plates_to_process:
        add_well_coords_to_df(int(pl), df)
    return df

def add_well_coords_to_df_from_file(expt_setup_dir, expt_setup_filename):
    os.chdir(expt_setup_dir)
    with open(expt_setup_filename) as datafile:
        expt_data = json.load(datafile)
    sample_data_dict = expt_data["sample_info"]
    return add_well_coords_to_df_from_sample_data_dict(sample_data_dict)

def add_well_coords_to_df_from_sample_data_dict(sample_data_dict):
    df = pd.DataFrame(sample_data_dict)
    unique_plates = list(df.Plate.unique())
    def pull_last_number(n):
        return n[-1:]
    plates_to_process = list(map(pull_last_number, unique_plates))
    for pl in plates_to_process:
        add_well_coords_to_df(int(pl), df)
    return df


# ----------
# Method to return a dictionary with 'x' and 'y' values for a single well based on a plate number and well id. 

whole_bedplate_positions = []

for p in ppc.plates:
    plate_dict = {}
    start_x = ppc.plate_start_position["x"] + (p["col"] * ppc.plate_column_offset)
    start_y = ppc.plate_start_position["y"] - (p["row"] * ppc.plate_row_offset)
    platewells =[]
    for i, well in enumerate(ppc.wells_in_plate):
        well_dict ={}
        well_dict["well_id"] = well['well_id']
        well_dict["x"] = start_x + (well["col"] * ppc.well_column_offset)
        well_dict["y"] = start_y - (well["row"] * ppc.well_row_offset)
        platewells.append(well_dict)
    plate_dict["plate"] = p['plate_id']
    plate_dict["well_dict"] = platewells
    whole_bedplate_positions.append(plate_dict)

 # bedplate_df = pd.DataFrame(whole_bedplate_positions) - Future work. To improve elegance create a dataframe and use locate to pull out wells rather than iterating through a list of nested dictionaries. 

def fetch_well_position(plate_num, well_id):
    coords = {}
    for p in whole_bedplate_positions:
        if str(plate_num) == str(p['plate']):
            for w in p["well_dict"]:
                if w['well_id'] == well_id:
                    coords['x'] = w['x']
                    coords['y'] = w['y']
    return(coords)


# ----------
# Method to take in a dataframe with different wells on each row, and a plate number and then add well coordinates to the dataframe. 

def add_well_coords_to_df(plate_num, df):
    well_coord_list_of_dicts = fetch_plate_wellpostions(plate_num)
#     print(well_coord_list_of_dicts)
#     plate_df = df.loc[df['Plate'] == f'Plate_{plate_num}']
    for index, row in df.iterrows():
#         print(row['Well'])
        for well in well_coord_list_of_dicts:
            if row['Plate'] == f'Plate_{plate_num}' and row['Well'] == well['well_id']:
                df.loc[index, 'x'] = well['x']
                df.loc[index, 'y'] = well['y']
                
                
def pull_list_of_well_coord_dicts_by_dfcolumn(df, column_to_group_by_string):    
    grouped_df = df.groupby([column_to_group_by_string]) #Returns a list of tuples with [0] being the group key and [1] the dataframe
    list_of_dicts = []

    for group in grouped_df:
        well_coords = []
        for index, row in group[1].iterrows():
            this_well = []
            this_well.append(row['x'])
            this_well.append(row['y'])
            well_coords.append(this_well)
        list_of_dicts.append({column_to_group_by_string : group[0], 'well-coords' : well_coords})
        
    return list_of_dicts
  
