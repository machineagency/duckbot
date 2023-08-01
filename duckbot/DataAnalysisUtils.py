import random
import pandas as pd
import utils.DuckbotExptSetupUtils as exp
import os
import json
import datetime
import pathlib
import re
import numpy as np
import cv2
from PIL import Image, ExifTags
# from plantcv import plantcv as pcv
import matplotlib
import matplotlib.pyplot as plt
import sys, traceback
import cv2
import numpy as np
import argparse
import string
from plantcv import plantcv as pcv
import pprint

def file_to_datetime(filename):
    no_file_ending = filename.split(".")[0]
    date = no_file_ending[-10:].split("-")
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    return year, month, day

def calculate_dpi(y, m, d, startdate):
    split_start_date = startdate.split("-")
    y0 = int(split_start_date[0])
    m0 = int(split_start_date[1])
    d0 = int(split_start_date[2])
    start = datetime.datetime(y0, m0, d0)
    end = datetime.datetime(y, m, d)
    diff = (end-start).days
    return(diff)

def find_plate_well_id(filename):
    well_id = re.search('well(.+?)_', filename).group(1) 
    #re.search looks for the string between the (). Within this a '.' indicates any character. '+?'Do something I don't fully understand
    #re.search returns a 'group' of information, which includes the actual matching string at position 0 or 1 depending on the search approach. 
    plate_section_of_string = re.search('late(.+?)_', filename).group(1) #Returns a subsection of the string that has the plate number
    plate_id = re.search('[0-9]', plate_section_of_string).group(0) #[0-9] finds numbers in a string
    return(f'Plate_{plate_id}_Well_{well_id}')

###IMAGE ANALYSIS

def return_df_with_image_data(img_data_dir, return_df_with_image_data, startdate):
    #Add dpi and green pixels
    df = pd.DataFrame(analyze_image_files(img_data_dir, return_df_with_image_data, startdate))
    return df

def analyze_image_files(img_data_dir, processed_img_dir_path, startdate):
    amount_green = []
    for file in os.listdir(img_data_dir):
        if ".jpg" in file:
            y, m, d = file_to_datetime(file)
            days_post_initiation = calculate_dpi(y, m, d, startdate)
            dpi= days_post_initiation
            plant_pixels = calculate_plant_pixels(img_data_dir, file, processed_img_dir_path)   
            amount_green.append({"filename": file, "dpi": dpi, "green_pixels": float(plant_pixels)})
    return(amount_green)

#Finds the pixels in the image that correspond to duckweed fronds and counts them
    
def calculate_plant_pixels(img_data_dir_path, file, processed_img_dir_path):
    os.chdir(img_data_dir_path)
    img, path, filename = pcv.readimage(filename=file)
    img_copy, path, filename = pcv.readimage(filename=file)
    plt.ioff()
    cropped_img = img[200:1050, 200:1050]
    if cropped_img == "Error":
        print(f"Error processing file {file}")
        duckweed_pixels = 0
    else:
        pcv.params.debug = False
        s = pcv.rgb2gray_hsv(cropped_img, 's')
        s_thresh = pcv.threshold.binary(s, 120, 255, 'light')
    #     cv2.imwrite(f'{processed_img_dir_path}/{filename}_processed_image_usedforpixelcount.jpg', s_cnt)
        objects, hierarchy = cv2.findContours(s_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
        objects = list(objects) # Cast tuple objects as a list
        duckweed_pixels = 0
        for i, cnt in enumerate(objects):
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt,True)
            roundness = area/(perimeter + 1) #To select for duckweed over lighting artefacts
            if area > 500 and roundness > 7.5: # can add stricter filters here as necessary
                print(f"perimeter: {perimeter}\n area: {area}")
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.circle(cropped_img, (cx, cy), 10, (255,0,0), -1) #Draws the little circle in the center of the object
                cv2.drawContours(cropped_img, objects, i, (255, 102, 255), 2, lineType=8, hierarchy=hierarchy)
                duckweed_pixels += area
        fig = plt.figure(figsize=(5, 10)); #semi-colon is intended to supress the output
        plt.subplot(211),plt.imshow(img_copy ,cmap = 'gray')
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(212),plt.imshow(cropped_img,cmap = 'gray')
        plt.title('Final processed image'), plt.xticks([]), plt.yticks([])
        fig_fname = f'{filename}_Imageprocessing_steps.jpg'
        os.chdir(processed_img_dir_path)
        plt.savefig(fig_fname)
    plt.ion()
    print(duckweed_pixels)
    return(duckweed_pixels)
            

#Looks for the outline of the well that the duckweed are in and crops to that outline. 
def circle_crop(file):
    img1 = cv2.imread(file)
    img = cv2.imread(file,0)
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 100, 150, cv2.THRESH_BINARY)
    # Create mask
    height,width = img.shape
    mask = np.zeros((height,width), np.uint8)
    cimg=cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    edges = cv2.Canny(thresh, 25, 100)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 100, param1 = 100, param2 = 30, minRadius = 325, maxRadius = 650)
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
    return(cropped_img)
            

def add_data_acrossdfs(input_value, shared_column_name, search_df, desired_column):
    df_subset = search_df[search_df[shared_column_name] == input_value][desired_column] #Find the desired column from the matching part of the search_df
    df_as_list = list(df_subset) #Convert to list to wipe clean the index carried over from search dataframe. 
    desired_value = df_as_list[0] #Specify that we want what should be a single value, rather than a whole list with one entry
    return desired_value

def plot_media_by_genotype(analysis_df, plot_title):
    genotype = np.unique(analysis_df["genotype"])
    media = np.unique(analysis_df["media"])
    for g in genotype:
        g_df = analysis_df[analysis_df["genotype"] == g]
        fig, ax = plt.subplots(figsize=(40, 20))
        for m in media:
            m_df = g_df[g_df["media"] == m]
            ax.errorbar(m_df['dpi'], m_df["median_green_pixels"],yerr=m_df["stdev_green_pixels"], label=g+"-"+m, linewidth=12)
        ax.legend(loc='upper right',fontsize='xx-large')
        fig.suptitle(f"{plot_title} - {g}", size = 25,wrap = False)
        ax.set_xlabel("Days post Initiation", size = 25)
        ax.set_ylabel("Frond area (pixels)", size = 25)
        ax.tick_params(axis='both', which='major', labelsize=15)
        fig.show()

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
                analysis_dict['dpi'].append(d[0])
                print(f"{g[0]}, {m[0]}, Day {d[0]}")
                print(list(d[1]['green_pixels']))
                cleaned_up_pixel_vals = remove_outliers(list(d[1]['green_pixels']))
                analysis_dict['green_pixels'].append(cleaned_up_pixel_vals)

    #Create dataframe and add medians and standard deviations. 
    analysis_df = pd.DataFrame(analysis_dict)
    analysis_df['median_green_pixels'] = analysis_df.apply(lambda row: np.median(row.green_pixels), axis = 1)
    analysis_df['stdev_green_pixels'] = analysis_df.apply(lambda row: np.std(row.green_pixels), axis = 1)
    return(analysis_df)

#Removes outliers (>2 stdevs from the mean) 
def remove_outliers(pixel_values):
    an_array = np.array(pixel_values)
    if len(an_array) > 1:
        mean = np.mean(an_array)
        standard_deviation = np.std(an_array)
        distance_from_mean = abs(an_array - mean)
        max_deviations = 2
        not_outlier = distance_from_mean < max_deviations * standard_deviation
        no_outliers = an_array[not_outlier]
    # #     not_zero = >0
    #     non_zero = no_outliers[no_outliers != 0]
        return no_outliers
    else:
        return an_array
    
    


