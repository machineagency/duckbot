import matplotlib
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import pyplot as plt


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
            m.dwell(t=500) #should be a 0.5 second pause to avoid drips between wells. 
        m.moveTo(z = z_dict["zero"])
        print("Move to Z = zero")
        m.moveTo(x=media_reservoir["x"], y=media_reservoir['y'])
        print("Move to reservoir position")
        m.move(de=-(dispense_offset * 2), s=1000)
        print("Empty excess media from syringe")
        
def visualize_plate_set_up(df_with_well_coords):
    
    #Establish a number of variables to be called in the matplotlib function below
    plates = list(np.unique(df_with_well_coords['Plate']))
    media_list = list(np.unique(df_with_well_coords['media']))
    c_num = 6 #How many columns per plate
    r_num = 4 #How many rows per plate
    column_list = list(np.arange(0, c_num))
    row_list = list(np.arange(0,r_num))

    date_today = "2022-08-09"
    row_dict ={"A" : 1, "B" :2, "C": 3, "D": 4, "E" : 5, "F" : 6}
    media_color_opts = ['lightcoral','lightblue','lightgreen','thistle','lightyellow','lightpink']
    media_color_dict = {}
    n = 0
    for m in media_list:
        media_color_dict[m] = media_color_opts[n]
        n = n + 1
    
    #Set up visualization using matplotlib
    for p in plates:
        fig, axs = plt.subplots(r_num, c_num, figsize=(12, 8))
        plt.suptitle(f"Set up plan for {p}", fontsize = 16)
        plate_df = df_with_well_coords.loc[df_with_well_coords['Plate'] == p]
        for c in column_list:
            for r in row_list:
                axs[r, c].set_xticks([])
                axs[r, c].set_yticks([])
        leg_patches = []
        for m in media_color_dict:
            m_patch = mpatches.Patch(color= media_color_dict[m])
            leg_patches.append(m_patch)
            media_df = plate_df.loc[plate_df['media'] == m]
            c = media_color_dict[m]
            for index, row in media_df.iterrows():
                well = row['Well'] #Find the pattern, use 'group(0)'' to pull string from match object and then slice to get desired part
                duckweed = row['genotype']
                row = row_dict[well[0]] - 1 #Pull column number from dictionary above. Adjust to start at 0 instead of 1
                column = int(well[1]) - 1
                ax_n = axs[row, int(column)]
                circle1 = plt.Circle((0.5, 0.5), 0.4, color=c)
                ax_n.add_patch(circle1)
                ax_n.text(0.5, 0.5, duckweed, horizontalalignment='center', verticalalignment='center', transform=ax_n.transAxes, weight='bold')
                ax_n.text(0.1, 0.9, well, horizontalalignment='center', verticalalignment='center', transform=ax_n.transAxes, weight='bold')
        fig.legend(handles = leg_patches, labels = media_list, loc = 'upper left')


