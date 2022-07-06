
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