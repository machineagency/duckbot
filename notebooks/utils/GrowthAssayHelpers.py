import os
import random
from pathlib import Path
import json
import re
import warnings
import pandas as pd
import numpy as np
import numpy as np
import datetime
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import cv2
from plantcv import plantcv as pcv
from science_jubilee.labware.Labware import Labware

## Notebook 1 Helpers
def assign_plates_and_wells(name, genotypes, media, reps, *labware):
    """Randomize replicates of duckweed genotype + media across given labware."""
    experiment_list = []
    for g in genotypes:
        for m in media:
            for x in range(reps):
                experiment_list.append({"genotype": g, "media": m, "condition_replicate": x + 1})

    required_wells = len(experiment_list)
    available_wells = 0
    plate_well_info = {}
    count = 0
    for plate_index, lw in enumerate(labware):
        if available_wells > required_wells:
            warnings.warn(f"Only plates 1 through {plate_index} are necessary for this experiment.")
            break
        available_wells += len(lw.wells)
        plate_type = lw.load_name
        for well in lw.wells:
            plate_well_info[count] = {}
            plate_well_info[count]['plate'] = f"plate_{plate_index}"
            plate_well_info[count]['plate_type'] = plate_type
            plate_well_info[count]['well'] = well
            count += 1
            
    # Confirm there are enough wells to run this experiment
    if available_wells < required_wells:
        raise Exception(f"Your experiment requires {required_wells} wells, but your labware provides only {available_wells} wells. Please add additional labware.")
    
    # Shuffle and assign to wells
    random.shuffle(experiment_list)
    for i, experimental_well in enumerate(experiment_list):
        well_info = plate_well_info[i]
        plate_id = well_info['plate']
        well_id = well_info['well']
        plate_type = well_info['plate_type']
        experimental_well['plate'] = plate_id
        experimental_well['plate_type'] = plate_type
        experimental_well['well'] = well_id
    
    return experiment_list

def visualize_plate_setup(experimental_config, *labware):
    """Visualize the growth assay plate setup based on a configuration file."""
    with open(experimental_config, 'r') as f:
        data = json.load(f)['sample_info']
    experiment_df = pd.DataFrame(data)
    plates = list(np.unique(experiment_df['plate']))
    media_list = list(np.unique(experiment_df['media']))

    # Pair each media type with a color
    # Note: limited to max of 6 media types based on this list.
    # We can add more colors here to accommodate larger experiments
    media_color_opts = ['lightcoral','lightblue','lightgreen','thistle','lightyellow','lightpink']
    media_color_dict = {}
    for i, m in enumerate(media_list):
        media_color_dict[m] = media_color_opts[i]

    # Iterate through each well of each plate
    for plate in plates:
        plate_df = experiment_df.loc[experiment_df['plate'] == plate]
        plate_type = np.unique(plate_df.plate_type)[0]
        labware = Labware(plate_type)
        column_num = len(labware.column_data)
        row_num = len(labware.row_data)
        column_list = list(np.arange(0, column_num))
        row_list = list(np.arange(0,row_num))

        fig, axs = plt.subplots(row_num, column_num, figsize=(12, 8))
        plt.suptitle(f"Set up plan for {plate}", fontsize = 16)
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
                well = row['well'] 
                duckweed = row['genotype']
                row = ord(well[0]) - 65 # convert row letter to number
                column = int(well[1:]) - 1
                ax_n = axs[row, int(column)]
                circle1 = plt.Circle((0.5, 0.5), 0.4, color=c)
                ax_n.add_patch(circle1)
                ax_n.text(0.5, 0.5, duckweed, horizontalalignment='center', verticalalignment='center', transform=ax_n.transAxes, weight='bold')
                ax_n.text(0.1, 0.9, well, horizontalalignment='center', verticalalignment='center', transform=ax_n.transAxes, weight='bold')
        fig.legend(handles = leg_patches, labels = media_list, loc = 'upper left')
    
    

######### Data Analysis Helpers
def make_df_with_images(image_dir_path, plate_setup_info):
    """Returns a dataframe which adds as a column the relevant image filename."""
    image_dir_path = Path(image_dir_path)
    experiment_df = pd.DataFrame(plate_setup_info)
    data_filenames = [x.stem for x in image_dir_path.glob('*.jpg')]
    filename_df = pd.DataFrame({"filename": data_filenames})
    filename_df['plate_well_id'] = filename_df.apply(lambda row: find_plate_well_id(row.filename), axis=1)
    filename_df['date'] = filename_df.apply(lambda row: row.filename[-10:], axis=1)

    data_df = pd.merge(filename_df, experiment_df, on="plate_well_id")
    return data_df

def find_plate_well_id(filename):
    # re.search looks for the string between the ().
    well_id = re.search('well(.+?)_', filename).group(1) 
    plate_section_of_string = re.search('late(.+?)_', filename).group(1) # get plate number
    plate_id = re.search('[0-9]', plate_section_of_string).group(0) #[0-9] finds numbers in a string
    return(f'plate_{plate_id}_well_{well_id}')

def file_to_datetime(filename):
    """Returns the year, month, and day given a filename in YYYY_MM_DD format."""
    no_file_ending = filename.split(".")[0]
    date = no_file_ending[-10:].split("-")
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    return year, month, day

def calculate_dpi(y, m, d, startdate):
    """Calculates days post initiation given 2 dates."""
    split_start_date = startdate.split("-")
    y0 = int(split_start_date[0])
    m0 = int(split_start_date[1])
    d0 = int(split_start_date[2])
    start = datetime.datetime(y0, m0, d0)
    end = datetime.datetime(y, m, d)
    diff = (end-start).days
    return(diff)

def analyze_images(img_data_dir, processed_img_dir_path, startdate):
    amount_green = []
    ten_percent = int(len(os.listdir(img_data_dir)) * 0.1)
    percent_done = 0
    for index, file in enumerate(os.listdir(img_data_dir)):
        # Update user on progress because this can take a while
        if (index > 0) and (index % ten_percent == 0):
            percent_done += 10
            print(f"{percent_done}% done processing images")
        
        if ".jpg" in file:
            y, m, d = file_to_datetime(file)
            days_post_initiation = calculate_dpi(y, m, d, startdate)
            dpi= days_post_initiation
            plant_pixels = calculate_plant_pixels(img_data_dir, file, processed_img_dir_path)   
            amount_green.append({"filename": file, "dpi": dpi, "green_pixels": float(plant_pixels)})
    print("Done processing images!")
    return pd.DataFrame(amount_green)

#Finds the pixels in the image that correspond to duckweed fronds and counts them
def calculate_plant_pixels(img_data_dir_path, file, processed_img_dir_path):
    os.chdir(img_data_dir_path)
    img, path, filename = pcv.readimage(filename=file)
    img_copy, path, filename = pcv.readimage(filename=file)
    plt.ioff()
    cropped_img = img[200:1050, 200:1050]
    # if cropped_img == "Error":
    if cropped_img is None:
        print(f"Error processing file {file}")
        duckweed_pixels = 0
    else:
        pcv.params.debug = False
        s = pcv.rgb2gray_hsv(cropped_img, 's')
        s_thresh = pcv.threshold.binary(s, 120, 'light')
    #     cv2.imwrite(f'{processed_img_dir_path}/{filename}_processed_image_usedforpixelcount.jpg', s_cnt)
        objects, hierarchy = cv2.findContours(s_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
        objects = list(objects) # Cast tuple objects as a list
        duckweed_pixels = 0
        for i, cnt in enumerate(objects):
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt,True)
            roundness = area/(perimeter + 1) #To select for duckweed over lighting artefacts
            if area > 500 and roundness > 7.5: # can add stricter filters here as necessary
                # print(f"perimeter: {perimeter}\n area: {area}")
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.circle(cropped_img, (cx, cy), 10, (255,0,0), -1) #Draws the little circle in the center of the object
                cv2.drawContours(cropped_img, objects, i, (255, 102, 255), 2, lineType=8, hierarchy=hierarchy)
                duckweed_pixels += area
        fig = plt.figure(figsize=(5, 10)); #semi-colon is intended to supress the output
        plt.subplot(211), plt.imshow(img_copy, cmap = 'gray')
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(212),plt.imshow(cropped_img,cmap = 'gray')
        plt.title('Final processed image'), plt.xticks([]), plt.yticks([])
        fig_fname = f'{filename}_Imageprocessing_steps.jpg'
        os.chdir(processed_img_dir_path)
        plt.savefig(fig_fname)
        plt.close(fig)
    return(duckweed_pixels)

def generate_analysis_df(pixel_df, data_df):
    pixel_df['filename_no_ext'] = pixel_df.apply(lambda row: row.filename[0:-4], axis=1)
    data_df['dpi'] = data_df.apply(lambda row: add_data_acrossdfs(row.filename, 'filename_no_ext', pixel_df, 'dpi'), axis = 1)
    data_df['green_pixels'] = data_df.apply(lambda row: add_data_acrossdfs(row.filename, 'filename_no_ext', pixel_df, 'green_pixels'), axis = 1)
    data_df = data_df.loc[pixel_df['green_pixels'] != 0.0]
    #Create new dictionary
    analysis_dict = {'genotype': [], 'media' : [], 'dpi' : [], 'green_pixels': []}

    #Populate dictionary with values from dataframe constructed above
    genotype_df = data_df.groupby(['genotype']) #Returns a list of tuples with [0] being the group key and [1] the dataframe
    for g in genotype_df:
        media_df = g[1].groupby(['media'])
        for m in media_df:
            dpi_df = m[1].groupby(['dpi'])
            for d in dpi_df:
                analysis_dict['genotype'].append(list(d[1]['genotype'])[0])
                analysis_dict['media'].append(list(d[1]['media'])[0])
                analysis_dict['dpi'].append(d[0][0])
                cleaned_up_pixel_vals = remove_outliers(list(d[1]['green_pixels']))
                analysis_dict['green_pixels'].append(cleaned_up_pixel_vals)

    #Create dataframe and add medians and standard deviations. 
    analysis_df = pd.DataFrame(analysis_dict)
    analysis_df['median_green_pixels'] = analysis_df.apply(lambda row: np.median(row.green_pixels), axis = 1)
    analysis_df['stdev_green_pixels'] = analysis_df.apply(lambda row: np.std(row.green_pixels), axis = 1)
    return(analysis_df)

def add_data_acrossdfs(input_value, shared_column_name, search_df, desired_column):
    df_subset = search_df[search_df[shared_column_name] == input_value][desired_column] #Find the desired column from the matching part of the search_df
    df_as_list = list(df_subset) #Convert to list to wipe clean the index carried over from search dataframe. 
    desired_value = df_as_list[0] #Specify that we want what should be a single value, rather than a whole list with one entry
    return desired_value


def remove_outliers(pixel_values):
    """Remove outliers (>2 stdevs from the mean)""" 
    an_array = np.array(pixel_values)
    if len(an_array) > 1:
        mean = np.mean(an_array)
        standard_deviation = np.std(an_array)
        distance_from_mean = abs(an_array - mean)
        max_deviations = 2
        not_outlier = distance_from_mean < max_deviations * standard_deviation
        no_outliers = an_array[not_outlier]
        return no_outliers
    else:
        return an_array
    
def generate_growth_curves(analysis_df):
    genotype = np.unique(analysis_df["genotype"])
    media = np.unique(analysis_df["media"])

    for g in genotype:
        g_df = analysis_df[analysis_df["genotype"] == g]
        fig, ax = plt.subplots(figsize=(40, 20))
        
        i = 0
        colors = ['#648FFF', '#DC267F', '#FE6100', '#FFB000']
        ls = ['-','--','-.',':']
        for m in sorted(media, key=len): # to make sure it's presented in the right order
            m_df = g_df[g_df["media"] == m]
            ax.errorbar(m_df['dpi'], m_df["median_green_pixels"], label=g+"-"+m, linewidth=12, color=colors[i], alpha=0.7)
            plt.fill_between(m_df['dpi'], m_df["median_green_pixels"] - m_df["stdev_green_pixels"], m_df["median_green_pixels"]+m_df["stdev_green_pixels"], color=colors[i], alpha=0.3)
            i+=1
        ax.legend(loc='upper left',
            ncol=1, fancybox=True, shadow=True, fontsize=50, labels=["0mM", "25mM", "50mM", "100mM"])
        fig.suptitle(f"{g} Growth Curve", size = 100, wrap = False)
        ax.set_xlabel("Days post Initiation", size = 75)
        ax.set_ylabel("Frond area (pixels)", size = 75)
        ax.tick_params(axis='both', which='major', labelsize=25)
        plt.ticklabel_format(axis='y', style='sci', scilimits=(4,4))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig(f'/Users/blairsubbaraman/Downloads/{g}-testing.jpg')
    