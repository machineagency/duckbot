#Absolute values (07/19/22)
#Plate 1, well A1 - X - 32.0, Y - 273. 
#Distance between columns (X - 19)
#Distance between rows (Y - 19)
#Distance between plate positions A1 in same column (Y - (270 -173) = 97
#Distance between plate positions A1 in different column (X - (166-25) = 141)
#Offset for the 50 ml Syringe tool (X minus 4 , Y minus 5 , Z is -50 for the bed offset for the smaller syringe tool).  #Note that this already incorporates legacy offsets built into duet for the smaller syringe tool. 



#Note that these dimensions have been established according to the specifications of the specific bedplate and 24 well plates we were using. 

bedplate_z_offest = 10
plate_column_offset = 141
plate_row_offset = 97

well_column_offset = 19
well_row_offset = 19

plate_start_position = {"x" : 27, "y" : 267}
#Plate 1 is defined her as the one diagonally opposite from the power supply.
#The way we have the bedplate set up is basically upside down relative to what the Duetboard is expecting. So instead of calculating our y up from zero we go down from 300. 

plates = [{"plate_id": 1, "col": 0, "row": 1},
          {"plate_id": 2, "col": 0, "row": 2},
          {"plate_id": 3, "col": 1, "row": 0},
          {"plate_id": 4, "col": 1, "row": 1},
          {"plate_id": 5, "col": 1, "row": 2}]



wells_in_plate= [{"well_id" : "A1", "col": 0, "row": 0}                          ,
                 {"well_id" : "A2", "col": 1, "row": 0},
                 {"well_id" : "A3", "col": 2, "row": 0},
                 {"well_id" : "A4", "col": 3, "row": 0},
                 {"well_id" : "A5", "col": 4, "row": 0},
                 {"well_id" : "A6", "col": 5, "row": 0},
                 {"well_id" : "B1", "col": 0, "row": 0},
                 {"well_id" : "B2", "col": 1, "row": 1},
                 {"well_id" : "B3", "col": 2, "row": 1},
                 {"well_id" : "B4", "col": 3, "row": 1},
                 {"well_id" : "B5", "col": 4, "row": 1},
                 {"well_id" : "B6", "col": 5, "row": 1},
                 {"well_id" : "C1", "col": 0, "row": 2},
                 {"well_id" : "C2", "col": 1, "row": 2},
                 {"well_id" : "C3", "col": 2, "row": 2},
                 {"well_id" : "C4", "col": 3, "row": 2},
                 {"well_id" : "C5", "col": 4, "row": 2},
                 {"well_id" : "C6", "col": 5, "row": 2},
                 {"well_id" : "D1", "col": 0, "row": 3},
                 {"well_id" : "D2", "col": 1, "row": 3},
                 {"well_id" : "D3", "col": 2, "row": 3},
                 {"well_id" : "D4", "col": 3, "row": 3},
                 {"well_id" : "D5", "col": 4, "row": 3},
                 {"well_id" : "D6", "col": 5, "row": 3}]


# ----------
# Method to return an updated version of the wells_in_plate dictionary defined above
# with 'x' and 'y' values added into each well dictionary, calculated for the specific plate. 

def fetch_plate_wellpostions(plate_num):
    plate_of_interest = next(p for p in plates if p["plate_id"] == plate_num)
    start_x = plate_start_position["x"] + (plate_of_interest["col"] * plate_column_offset)
    start_y = plate_start_position["y"] - (plate_of_interest["row"] * plate_row_offset)
    for i, well in enumerate(wells_in_plate):
        well["x"] = start_x + (well["col"] * well_column_offset)
        well["y"] = start_y - (well["row"] * well_row_offset)
    return(wells_in_plate)


# ----------
# Method to return a dictionary with 'x' and 'y' values for a single well based on a plate number and well id. 

whole_bedplate_positions = []

for p in plates:
    plate_dict = {}
    start_x = plate_start_position["x"] + (p["col"] * plate_column_offset)
    start_y = plate_start_position["y"] - (p["row"] * plate_row_offset)
    for i, well in enumerate(wells_in_plate):
        well["x"] = start_x + (well["col"] * well_column_offset)
        well["y"] = start_y - (well["row"] * well_row_offset)
    plate_dict["plate"] = p['plate_id']
    plate_dict["well_dict"] = wells_in_plate
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
