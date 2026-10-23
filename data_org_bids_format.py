################################## data organisation and bids formating ##############################################
# in this script we organise the data, convert it to bids format and save the information in a data table to be used during preprocessing

# load packages
import pandas as pd
import numpy as np
import os
import re
import dicom2nifti
import dicom2nifti.settings as settings
from pathlib import Path
import yaml

# load working directories
project_dir = Path(r"C:\Users\dsteenke\PycharmProjects\data_structuring")
config_path = project_dir / "config.local.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
settings = config["dcm_bids_df"]
# define them
main_folder = settings["main_folder"]
project_folder = settings["project_folder"]
output_folder = settings["output_folder"]

# scan times
scan_times = ['UCBH_Baseline', 'UCBH_Day30']
# tracer
tracer = 'ucbh'
# conditions
conditions = ['ChronicVLAnimals'] # the folders are saved with 2 for the second cohort
# cohorts
cohorts = ['Cohort3']
# define which animal had which intervention
id_map = {
    "ChronicVLAnimals": range(1,13)     # IDs 1-12
    #"ControlAnimals": range(1, 7),     # IDs 1–6
    #"AcuteVLAnimals": range(7, 13),    # IDs 7–12
}

data_entries = []
columns = ['project', 'subject', 'session', 'project_abv', 'condition', 'tracer', 'image_type', 'pet', 'ct', 'filename_pet', 'filename_ct']

# this is a function that counts the number of files in a folder
def files_num(folder_path):
    files = os.listdir(folder_path) # goes into the folder
    files_len = len(files) # counts the number of files
    return files_len # returns the number

# condition, session, subject, ct, pet for the data frame
cond = None
ses = None
sub = None
ct = None
pet = None

# loop through cohorts
for cohort in cohorts:
    cohort_folder = os.path.join(main_folder, project_folder, cohort)
    print(cohort_folder)

    offset = 0 if cohort == "Cohort1" else 24 # adapt offset based on the cohort, in this study 3 cohorts and data collected at different time points

    for condition in conditions:

        if condition == 'AcuteVLAnimals':
            cond = 'acute'
        elif condition == 'ChronicVLAnimals':
            cond = 'chronic'
        else:
            cond = 'control'

        if cohort == 'Cohort3':
            condition_folder = os.path.join(cohort_folder, condition)
        else:
            condition_folder = os.path.join(cohort_folder, f'{condition}2') # if more than one cohort was processed at the time and needs to be added as a list above
        print(condition_folder)

        # loop through sessions
        for session in scan_times:
            ses_folder = os.path.join(condition_folder, session) # session folder
            print(ses_folder)

            if os.path.exists(ses_folder): # if session folder exist define the scan time
                if session == 'UCBH_Baseline':
                    ses = 'ses-Baseline'
                elif session == 'UCBH_Day30':
                    ses = 'ses-d30'

                # based on the id and condition define the subj id
                for i in id_map[condition]:
                    sub_id = f"ID{i}"
                    sub = f"sub-{i + offset:02d}"  # SINGLE source of truth
                    sub_folder = os.path.join(ses_folder, sub_id)
                    print(sub_folder)

                    if os.path.exists(sub_folder):
                        folder1 = os.path.join(sub_folder, 'DICOM', 'PA1', 'ST1', 'SE1') # folder where dicom files are, unknown if pet or ct
                        folder2 = os.path.join(sub_folder, 'DICOM', 'PA1', 'ST1', 'SE2') # folder where dicom files are, unknown if pet or ct

                        if os.path.exists(folder1) and os.path.exists(folder2): # if both folders exist
                            print('both folders exist')
                            ct = 1 # to add the df
                            pet = 1 # to add the df
                            if files_num(folder1) > files_num(folder2): # which folder has more files -> ct
                                CT = folder1
                                PET = folder2
                            else:
                                PET = folder1
                                CT = folder2
                        if os.path.exists(folder1) and not os.path.exists(folder2): # if only one folder exists, above 300 files ct, otherwise pet
                            if files_num(folder1) > 300:
                                CT = folder1
                                print('CT exists')
                                ct = 1
                                pet = 0
                            else:
                                PET = folder1
                                print('PET exists')
                                pet = 1
                                ct = 0
                        elif not os.path.exists(folder1) and os.path.exists(folder2):
                            if files_num(folder2) > 300:
                                CT = folder2
                                print('CT exists')
                                ct = 1
                                pet = 0
                            else:
                                PET = folder2
                                print('PET exists')
                                pet = 1
                                ct = 0

                        nii_PET = os.path.join(main_folder, output_folder, sub, ses, 'pet') # define folder
                        os.makedirs(nii_PET, exist_ok=True)
                        nii_CT = os.path.join(main_folder, output_folder, sub, ses, 'ct') # define folder
                        os.makedirs(nii_CT, exist_ok=True)

                        pet_fname = f'{sub}_{ses}_trc-ucbh_VL_{cond}_rec-stat_pet.nii.gz' # define pet filename
                        ct_fname = f'{sub}_{ses}_trc-ucbh_VL_{cond}_rec-stat_ct.nii.gz' # ct filename

                        rename_pet_file = os.path.join(nii_PET, pet_fname) # to rename pet imake like bids after dc2nii conversion
                        rename_ct_file = os.path.join(nii_CT, ct_fname) # to rename ct imake like bids after dc2nii conversion

                        if os.path.exists(CT) and os.path.exists(PET): # if both folders exist
                            try:
                                dicom2nifti.convert_directory(PET, nii_PET, reorient=False, compression=True) # convert pet dcm2nii
                                dicom2nifti.convert_directory(CT, nii_CT, reorient=False, compression=True) # convert ct dcm2nii
                                pet_file = os.path.join(nii_PET, os.listdir(nii_PET)[0]) # get pet file
                                ct_file = os.path.join(nii_CT, os.listdir(nii_CT)[0]) # get ct file
                                os.replace(pet_file, rename_pet_file) # rename pet filename
                                os.replace(ct_file, rename_ct_file) # rename ct filename
                                print(f'{rename_pet_file} and {rename_ct_file} converted')
                            except Exception:
                                print('an error occured')

                        elif not os.path.exists(CT) and os.path.exists(PET): # if only PET folder exists
                            try:
                                dicom2nifti.convert_directory(PET, nii_PET, reorient=False, compression=True)
                                pet_file = os.path.join(nii_PET, os.listdir(nii_PET)[0])
                                os.replace(pet_file, rename_pet_file)
                                print(f'{rename_pet_file} converted')
                            except Exception:
                                print('an error occured')

                        elif not os.path.exists(PET) and os.path.exists(CT): # if only CT folder exists
                            try:
                                dicom2nifti.convert_directory(CT, nii_CT, reorient=False, compression=True)
                                ct_file = os.path.join(nii_CT, os.listdir(nii_CT)[0])
                                os.replace(ct_file, rename_ct_file)
                                print(f'{rename_ct_file} converted')
                            except Exception:
                                print('an error occured')
                        else:
                            print('both folders do not exist') # if none exists

                        project = '2026_Acute_Chronic_Plasticity' # define project name
                        project_abv = 'VL' # project abv
                        image_type = 'stat' # image type statci or dynamic
                        tracer = 'ucbh' # tracer
                        data_entries.append(
                            [project, sub, ses, project_abv, cond, tracer, image_type, pet, ct, pet_fname, ct_fname])  # append all infos
                    else:
                        print(f'{sub_folder} does not exist')
            else:
                print(f'{ses_folder} does not exist')

df = pd.DataFrame(data_entries, columns=columns) # convert infos to a df
excel_file = os.path.join(main_folder, output_folder, "cohort3_ucbh_VL_data.xlsx") # excel file
df.to_excel(excel_file, index=False) # save file