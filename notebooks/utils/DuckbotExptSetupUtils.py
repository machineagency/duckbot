 
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

def chunk_list(well_list, n):
    for i in range(0, len(well_list), n):    # looping till length l
        yield well_list[i:i + n]
        
def dispense_to_wells(m, well_coords, dispense_offset, dispenses_per_syringe_fill, media_reservoir, z_dict): 
    dispense_chunks = list(chunk_list(well_coords, int(dispenses_per_syringe_fill)))
    for wells in dispense_chunks:
        m.moveTo(z = z_dict["zero"])
        print("Move to Z = zero")
        m.moveTo(x=media_reservoir["x"], y=media_reservoir['y'])
        print("Move to reservoir position")
        m.moveTo(z=z_dict["aspirate"])
        print("moved to height for aspiration")
       # m.move(de=dispense_offset * dispenses_per_syringe_fill)
        m.move(de=dispense_offset * (len(wells) + 2), s=1000)
        m.moveTo(z = z_dict["zero"])
        print("Moved to Z = zero")
        m.moveTo(x=wells[0][0], y = wells[0][1], z = z_dict["dispense"])
        print("Hovering over the first well to dispense into")
        for well in wells:
            print("Prepare to dispense")
            print(f"X = {well[0]}")
            print(f"Y = {well[1]}")     
            m.moveTo(x=well[0], y=well[1])
            m.move(de=-dispense_offset, s=1000)
        m.moveTo(z = z_dict["zero"])
        print("Move to Z = zero")
        m.moveTo(x=media_reservoir["x"], y=media_reservoir['y'])
        print("Move to reservoir position")
        m.move(de=-(dispense_offset * 2), s=1000)
        print("Empty excess media from syringe)
        
        

