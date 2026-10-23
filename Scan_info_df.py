######################################### creating a data frame ##################################################
# in this script we crate a data frame including subj ids, scan times, ct and pet scan existance, project name, scanner name ect.

# import the packages
import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
import yaml

project_dir = Path(r"C:\Users\dsteenke\PycharmProjects\data_structuring")
config_path = project_dir / "config.local.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
settings = config["df_creation"]

main_folder = settings["main_folder"]
data_type = settings["data_type"]
project_folders = settings["project_folders"]
condition_folders = settings["condition_folders"]
scanner = settings["scanner"]
data_entries = [] # to save the data info
# Initialize the DataFrame, name the columns
columns = ['Project_Name', 'Subject_ID', 'Tracers', 'Scan_Time', 'Condition','Injected_Dose', 'Dose_Uptake', 'Image_Type_DICOM', 'Image_Type_NIFTI', 'Modality_CT', 'Modality_PET', 'Scanner_Name', 'Image_Path']
Data_information_table = pd.DataFrame(columns=columns)

# Function to extract numeric values from 'dX' or 'dX-Y' formats
# So that we can have the scan time in an ascending order
def extract_numbers(scan):
    numbers = re.findall(r'\d+', scan)  # Extract all numbers
    return list(map(int, numbers))  # Convert to integers

# Iterate over project folders
for folder in project_folders:

    project_folder = os.path.join(main_folder, data_type[0], folder)  # Create project path
    project_name = folder  # to add the project name to the data list later

    if os.path.exists(project_folder):  # Check if folder exists
        ids = os.listdir(project_folder)  # List subjects in the folder
        sorted_ids = sorted(ids, key=lambda x: int(''.join(filter(str.isdigit, x))))  # Sort numerically the IDs

        for subj_id in sorted_ids:  # Loop through the sorted subject ids
            subj_folder = os.path.join(project_folder, subj_id)  # Create subject path
            tracers = os.listdir(subj_folder)  # List tracers in the subject folder

            sorted_sub_id = subj_id  # to add the ID to the data list

            for tracer in tracers:  # Loop through each tracer
                tracer_name = []  # define an obejct to save the tracer
                tracer_name = tracer  # save the tracer

                scan_folder = os.path.join(subj_folder, tracer)  # Path to tracer folder
                scan_times = os.listdir(scan_folder)  # Get scan times from the tracer folder
                sorted_scan_times = sorted(scan_times, key=extract_numbers)  # Sort scan times
                # print(sorted_scan_times)  # print sorted scan times

                for time in sorted_scan_times:  # loop through scan times
                    scan_time = []  # define an obejct to save the scan times
                    scan_time = time  # save the time
                    scan_time_path = os.path.join(scan_folder, time)  # create path for each scan time folder
                    # print(scan_time_path)

                    condition = []  # empty list to add the conditions

                    if folder in condition_folders:  # if the projects have conditions
                        condition_list = os.listdir(scan_time_path)  # get the condition folder name
                        condition = condition_list[0]  # get the name of the condition
                        # print(condition)

                        condition_folder = os.path.join(scan_time_path,
                                                        condition_list[0])  # create path for condition folder
                        # print(condition_folder)

                        image_type_list = os.listdir(
                            condition_folder)  # go into the condition folder to get the data type DICOM/NIFTI
                        # print(image_type_list)

                        for image in image_type_list:  # loop through the DICOM and NIFTI folders
                            image_type_DICOM = []  # define an obejct to save the DICOM
                            image_type_NIFTI = []  # define an obejct to save the NIFTI

                            if image == 'DICOM':  # if the modality is dicom create a path for it
                                image_folder = os.path.join(condition_folder, image)
                                image_type_DICOM = 'DICOM'
                            else:  # if it is not dicom create a path for nifti
                                image_folder = os.path.join(condition_folder, image)
                                image_type_NIFTI = 'NIFTI'

                            scanner_modality = os.listdir(image_folder)  # go into modality folder PET/CT

                            for modality in scanner_modality:  # loop through each modality folder
                                modality_CT = []  # define an obejct to save the CT
                                modality_PET = []  # define an obejct to save the PET
                                modality_folder = os.path.join(image_folder,
                                                               modality)  # create path for the modality folders

                                # save them based on their modality
                                if modality == 'CT':
                                    modality_CT = 'CT'
                                else:
                                    modality_PET = 'PET'

                                # if the modality and the NIFTI folders exist
                                if os.path.exists(modality_folder) and image == 'NIFTI':
                                    files = os.listdir(modality_folder)  # go into the folder
                                    print(files)
                                    file_path = os.path.join(modality_folder, files[0])  # join the path
                                    print(file_path)
                                else:
                                    file_path = None

                                # Append to the list
                                data_entries.append([
                                    project_name, sorted_sub_id, tracer_name,
                                    scan_time, condition, None, None, image_type_DICOM, image_type_NIFTI, modality_CT,
                                    modality_PET, scanner[0], file_path
                                ])

                    else:  # otherwise (if no condition) directly go into the scan time folder for the data type

                        image_type_list = os.listdir(scan_time_path)  # go into each scan time folder
                        print(image_type_list)

                        for image in image_type_list:  # loop through nifti and dicom
                            image_type_DICOM = []  # define dicom
                            image_type_NIFTI = []  # define nifti

                            if image == 'DICOM':  # if image is dicom create a path for it
                                image_folder = os.path.join(scan_time_path, image)
                                image_type_DICOM = 'DICOM'
                            else:  # if nifti create one for nifti
                                image_folder = os.path.join(scan_time_path, image)
                                image_type_NIFTI = 'NIFTI'

                            scanner_modality = os.listdir(image_folder)  # go into modality folder PET/CT

                            for modality in scanner_modality:  # loop through each modality folder

                                modality_CT = []  # define CT
                                modality_PET = []  # define PET
                                modality_folder = os.path.join(image_folder,
                                                               modality)  # create path for the modality folders

                                # save as CT ot PET
                                if modality == 'CT':
                                    modality_CT = 'CT'
                                else:
                                    modality_PET = 'PET'

                                # if modality and nifti exists get the path for the image
                                if os.path.exists(modality_folder) and image == 'NIFTI':
                                    files = os.listdir(modality_folder)
                                    print(files)
                                    file_path = os.path.join(modality_folder, files[0])
                                    print(file_path)
                                else:
                                    file_path = None

                                # Append to the list
                                data_entries.append([
                                    project_name, sorted_sub_id, tracer_name,
                                    scan_time, condition, None, None, image_type_DICOM, image_type_NIFTI, modality_CT,
                                    modality_PET, scanner[0], file_path
                                ])

# Convert list to DataFrame if there are entries
if data_entries:
    Data_information_table = pd.DataFrame(data_entries, columns=columns)
print(Data_information_table)

# save DataFrame to CSV, we can also save it as excel
csv_file_path = os.path.join(main_folder, data_type[0], "Data_information_table.csv")
Data_information_table.to_csv(csv_file_path, index=False)