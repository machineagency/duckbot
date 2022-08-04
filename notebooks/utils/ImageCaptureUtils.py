import utils.Plate_positions as pp #Local library

def move_to_first_well(plates_to_image):
    first_plate = plates_to_image[0]
    well = pp.fetch_well_position(first_plate,"A1")
    m.moveTo(x=well["x"], y=well["y"], z=10)
    
def create_well_dict(expt_setup_dir, expt_setup_filename):
    os.chdir(exp_setup_file_path)
    with open(expt_setup_file_name) as datafile:
        expt_data = json.load(datafile)
    sample_data = expt_data["sample_info"]
    df = pd.DataFrame(sample_data)
    unique_plates = list(df.Plate.unique())
    def pull_last_number(n):
        return n[-1:]
    plates_to_image = list(map(pull_last_number, unique_plates))
    print(f"Plates to image: {plates_to_image}")
    for pl in plates_to_image:
        pp.add_well_coords_to_df(int(pl), df)
    return df

def pull_plates_to_image(expt_setup_dir, expt_setup_filename):
    os.chdir(exp_setup_file_path)
    with open(expt_setup_file_name) as datafile:
        expt_data = json.load(datafile)
    sample_data = expt_data["sample_info"]
    df = pd.DataFrame(sample_data)
    unique_plates = list(df.Plate.unique())
    def pull_last_number(n):
        return n[-1:]
    plates_to_image = list(map(pull_last_number, unique_plates))
    return plates_to_image

def image_plates(df_with_well_coords, output_data_dir):
    for index, row in df_with_well_coords.iterrows():
        plate = row['Plate_id']
        well = row['Well']
        well_x = row['x'] 
        well_y = row['y']
        print(f'move to well {well}')
        m.moveTo(x=well_x, y=well_y, z=10)
        m.dwell(500) #dwell .75 seconds
        print('get frame')
        f = getFrame()
        print('write image to file')
        cv2.imwrite(f'{output_data_dir}/plate{plate}_well{well}_{date.today()}.jpg', f)
        time.sleep(0.25)