#Absolute values (07/19/22)
#Plate 1 is defined her as the one kitty corner from the power supply.
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

plate_start_position = {"x" : 27, "y" : 267}#The way we have the bedplate set up is basically upside down relative to what the Duetboard is expecting. So instead of calculating our y up from zero we go down from 300. 

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

def fetch_plate_wellpostions(plate_num):
    plate_of_interest = next(p for p in plates if p["plate_id"] == plate_num)
    start_x = plate_start_position["x"] + (plate_of_interest["col"] * plate_column_offset)
    start_y = plate_start_position["y"] - (plate_of_interest["row"] * plate_row_offset)
    for i, well in enumerate(wells_in_plate):
        well["x"] = start_x + (well["col"] * well_column_offset)
        well["y"] = start_y - (well["row"] * well_row_offset)
    return(wells_in_plate)


    

# for i, x in enumerate(well_series):
#     x["gcode_coordinates"] = "G1 x{0} y{1}  F6000\n".format((plate_start_position["x"] + x["x-offset"]),(plate_start_position["y"] + x["y-offset"]))
#     print("Moving to well {}".format(x["well_id"]))
#     byte_coords = bytes(x["gcode_coordinates"], 'utf-8')
#     ser.write(byte_coords)
#     ser.write(b'G4 P2000') #Adds a 2 second pause just to make the movements visually trackable. 
#     print(byte_coords)