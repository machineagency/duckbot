import utils.PlatePositionUtils as pp #Local library
import cv2 as cv2
import os 
import json
import pandas as pd
import utils.CameraUtils as cu #Local library. #Note that this library requirs a package that can only be installed on raspbery pi. 
import datetime
from datetime import date
import time


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
        f_rgb = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'{output_data_dir}/{expt_name}_{plate}_well{well}_{date.today()}.jpg', f_rgb)
        images.append(f)
        time.sleep(0.1)