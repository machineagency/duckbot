import utils.PlatePositionUtils as pp #Local library
import cv2 as cv2
import os 
import json
import pandas as pd
import utils.CameraUtils as cu #Local library. #Note that this library requirs a package that can only be installed on raspbery pi. 
import datetime
from datetime import date
import time
import numpy as np
import re
import PIL as Image
import matplotlib.image as mpimg
import matplotlib
matplotlib.use('TkAgg') #This is a specific back end of matplotlib 
from matplotlib import pyplot as plt


def move_to_first_well(m, plates_to_image):
    first_plate = plates_to_image[0]
    well = pp.fetch_well_position(first_plate,"A1")
    m.moveTo(x=well["x"], y=well["y"], z=10)
    

def pull_plates_to_image(expt_setup_dir, expt_setup_filename):
    os.chdir(expt_setup_dir)
    with open(expt_setup_filename) as datafile:
        expt_data = json.load(datafile)
    sample_data = expt_data["sample_info"]
    df = pd.DataFrame(sample_data)
    unique_plates = list(df.Plate.unique())
    def pull_last_number(n):
        return n[-1:]
    plates_to_image = list(map(pull_last_number, unique_plates))
    return plates_to_image

def image_plates(m, df_with_well_coords, output_data_dir, expt_name):
    images = []
    
    for index, row in df_with_well_coords.iterrows():
        plate = row['Plate']
        well = row['Well']
        well_x = row['x'] 
        well_y = row['y']
        print(f'Imaging well {well}')
        m.moveTo(x=well_x, y=well_y, z=10)
        m.dwell(500) #dwell .75 seconds
        f = cu.getFrame()
        f_rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        cv2.imwrite(f'{output_data_dir}/{expt_name}_{plate}_well{well}_{date.today()}.jpg', f_rgb)
        images.append(f)
        time.sleep(0.1)
        
        
def create_plate_image_grid(df_with_well_coords, output_data_dir):
    plates = list(np.unique(df_with_well_coords['Plate']))
    plates = [int(x[-1]) for x in plates]
    c_num = 6 #How many columns per plate
    r_num = 4 #How many rows per plate
    row_dict ={"A" : 1, "B" :2, "C": 3, "D": 4, "E" : 5, "F" : 6}
    for p in plates:
        fig, axs = plt.subplots(r_num, c_num, figsize=(15, 10))
        plt.suptitle(f"Images captured from Plate {p}", fontsize = 16)
        os.chdir(output_data_dir)
        for file in os.listdir(output_data_dir):
            if ".jpg" and str(date.today()) in file:
                well = re.search("well..", file).group(0)[-2:] #Find the pattern, use 'group(0)'' to pull string from match object and then slice to get desired part
                plate = re.search("Plate\_.",file).group(0)[-1]
                well = well[-2:]
                row = row_dict[well[0]] - 1 #Pull column number from dictionary above. Adjust to start at 0 instead of 1
                column = int(well[1]) - 1
                if plate == str(p):
                    img = mpimg.imread(file)
#                     plt.imshow(img)
    #                 plt.axis('off')
                    axs[row, int(column)].axis('off')
                    axs[row, int(column)].imshow(img)
                    axs[row, int(column)].set_title(f"Plate{p}_{well}", fontsize = 8)