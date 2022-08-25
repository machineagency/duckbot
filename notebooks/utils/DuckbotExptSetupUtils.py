import matplotlib
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import pyplot as plt
import random
import json
from plantcv import plantcv as pcv

import utils.PlatePositionUtils as pp
import platform
if platform.system() == 'Linux':
    from utils.CameraUtils import * # this library can only be used on the RPi




def chunk_list(well_list, n):
    for i in range(0, len(well_list), n):    # looping till length l
        yield well_list[i:i + n]
        
def dispense_to_wells(m, well_coords, dispense_offset, dispenses_per_syringe_fill, media_reservoir, z_dict): 
    dispense_chunks = list(chunk_list(well_coords, int(dispenses_per_syringe_fill)))
    for wells in dispense_chunks:
        print("Dispensing media, please wait")
        m.moveTo(z = z_dict["zero"])
#         print("Move to Z = zero")
        m.moveTo(x=media_reservoir["x"], y=media_reservoir['y'])
#         print("Move to reservoir position")
        m.moveTo(z=z_dict["aspirate"])
#         print("moved to height for aspiration")
       # m.move(de=dispense_offset * dispenses_per_syringe_fill)
        m.move(de=dispense_offset * (len(wells) + 2), s=1000)
        m.moveTo(z = z_dict["zero"])
#         print("Moved to Z = zero")
        m.moveTo(x=wells[0][0], y = wells[0][1], z = z_dict["dispense"])
#         print("Hovering over the first well to dispense into")
        for well in wells:
#             print("Prepare to dispense")
#             print(f"X = {well[0]}")
#             print(f"Y = {well[1]}")     
            m.moveTo(x=well[0], y=well[1])
            m.move(de=-dispense_offset, s=1000)
            m.dwell(t=500) #should be a 0.5 second pause to avoid drips between wells. 
        m.moveTo(z = z_dict["zero"])
#         print("Move to Z = zero")
        m.moveTo(x=media_reservoir["x"], y=media_reservoir['y'])
#         print("Move to reservoir position")
        m.move(de=-(dispense_offset * 2), s=1000)
#         print("Empty excess media from syringe")
    print("Media dispensing completed")
        
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
        
def inoculation_loop_transfer(m, df, duckweed_reservoir, z_dict):
    grouped_df = df.groupby('genotype')
    for field_value, sample_df in grouped_df:
        print("Place container of duckweed type **{0}** into jubilee and ensure lid is open".format(field_value))
        print("""Type anything into the input field to confirm that the media is available.
        After this point the Jubilee will begin dispensing""")
        input() 
        count = 0
        for index,s in sample_df.iterrows():
            # move to a random point in the reservoir
            r = 20
            rx = random.randint(-r, r)
            ry = random.randint(-r, r)

            # move in xy first
            m.moveTo(x=duckweed_reservoir[0] + rx, y=duckweed_reservoir[1] + ry)

            # dip into the reservoir
            m.moveTo(z=z_dict['collect'])
            # slowly sweep
            m.move(dx=5, s=100)
            m.move(dy=5, s=100)
            m.move(dz=10, s=250) # start moving slowly up
            m.moveTo(z=z_dict['move'])
            well = pp.fetch_well_position(s["Plate"][-1], str(s["Well"]))
            m.moveTo(x=well['x'], y=well['y'])
            m.moveTo(z=z_dict['transfer'])
            m.move(dx=3, s=100)
            m.move(dy=-3, s=100) # move in opposite direction
            m.dwell(250)
            m.moveTo(z=z_dict['move'], s=800)
                     
#Looks for the outline of the well that the duckweed are in and crops to that outline. 
def well_check_circle_crop(img):
    img1 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.medianBlur(gray, 5)
    ret, thresh = cv2.threshold(gray, 100, 150, cv2.THRESH_BINARY)
    # Create mask
    height, width, nslice = img.shape
    mask = np.zeros((height,width), np.uint8)
    cimg=cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    edges = cv2.Canny(gray, 25, 100)
    gain = 1
    for g in np.arange(gain, 10, 0.1):
        # find the right gain to find a single circle
        circles = cv2.HoughCircles(edges,
                                   cv2.HOUGH_GRADIENT,
                                   g,
                                   minDist=100,
                                   param1=100,
                                   param2=100,
                                   minRadius=325,
                                   maxRadius=650
                                   )
        if circles is None:
            continue
        numCircles = circles[0,:].shape[0]
        if numCircles == 1:
            break

    if circles is not None:
        i = circles[0][0]                
        # Draw on mask
        center = (int(i[0]),int(i[1]))
        radius = int(i[2])
        cv2.circle(mask,center,radius,(255,255,255),thickness=-1)
        # Copy that image using that mask
        masked_data = cv2.bitwise_and(img1, img1, mask=mask)
        # Apply Threshold
        _,thresh = cv2.threshold(mask,1,255,cv2.THRESH_BINARY)
        # Find Contour
        contours = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        x,y,w,h = cv2.boundingRect(contours[0][0])
        #   Crop masked_data
        cropped_img = masked_data[y:y+h,x:x+w]
    else:
        cropped_img = "Error"
    return(np.ascontiguousarray(cropped_img))

def identify_fronds(img):
    s = pcv.rgb2gray_hsv(img, 's')
    s_thresh = pcv.threshold.binary(s, 120, 255, 'light')
    objects, hierarchy = cv2.findContours(s_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    # Cast tuple objects as a list
    objects = list(objects)
    count = 0
    for i, cnt in enumerate(objects):
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt,True)
        if perimeter > 100 and area > 500: # can add stricter filters here as necessary
#             print(f"perimeter: {perimeter}\n area: {area}")
            count += 1
            # relevant for showing images; TODO: make this an function option
#             M = cv2.moments(cnt)
#             cx = int(M['m10']/M['m00'])
#             cy = int(M['m01']/M['m00'])
#             cv2.circle(crop, (cx, cy), 10, (255,0,0), -1)
#             cv2.drawContours(crop, objects, i, (255, 102, 255), 2, lineType=8, hierarchy=hierarchy)
    
    return count

                     
def check_wells(m, df):
    has_fronds = []
    for index, row in df.iterrows():
        plate = row['Plate']
        well = row['Well']
        well_x = row['x'] 
        well_y = row['y']
        print(f'Checking well {well}')
        m.moveTo(x=well_x, y=well_y, z=10)
        m.dwell(500) #dwell .75 seconds
        f = getFrame()
        crop = well_check_circle_crop(f)
        frond_check = identify_fronds(crop)
        if frond_check:
            has_fronds.append(True)
        else:
            print(f"Well {well} needs fronds")
            has_fronds.append(False)
        time.sleep(0.1)
    # update the df with the a new column
    df['hasFronds'] = has_fronds
    
def fill_empty_wells(m, df, duckweed_reservoir, z_dict):
    m.toolChange(4)
    empty = df.loc[df['hasFronds'] == False]
    inoculation_loop_transfer(m, empty, duckweed_reservoir, z_dict)
        


def add_input_to_json(notes, key, expt_setup_filepath):
    with open(expt_setup_filepath) as datafile:
        expt_data = json.load(datafile)
        expt_data[key] = notes
    with open(expt_setup_filename, 'w') as f:
        json.dump(expt_data, f)