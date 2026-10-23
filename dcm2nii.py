###################################### dcm to nii conversion ###########################################
# our data is reconstructed in a way that we do not know which folder contains the pet or the ct dicoms
# however we know approximately the number of dicoms and the folder containing dicoms below 300 files are PET, otherwise CT dicoms
# based on this information we organise the data structure and convert dicoms to nifti, without BIDS formating, which takes place in a separate script

#########################################################################################################
import nibabel as nib
import dicom2nifti
import pydicom
import os
import glob
import shutil
from pathlib import Path
import yaml

# loading paths from ymal file
project_dir = Path(r"C:\Users\dsteenke\PycharmProjects\data_structuring")
config_path = project_dir / "config.local.yaml"
with open(config_path, "r", encoding="utf-8") as f: # reading the file
    config = yaml.safe_load(f)
settings = config["dicom_conversion"] # selecting the defined paths
# adding them here
MainFolder = settings["MainFolder"]
SubFolder = settings["SubFolder"]
OutputFolder = settings["OutputFolder"]
SubOutputFolder = settings["SubOutputFolder"]

# Variables
Tracer = ['FDG', 'UCBH'] # type of tracer
ScanTime_FDG = ['BL', 'd1', 'd3', 'd7', 'd14', 'd21', 'd30'] # the scan time for FDG
ScanTime_UCBH = ['Baseline', 'w1', 'w2', 'w3', 'w4', 'w5', 'w7', 'w9'] # the scan time for UCBH
OrgTime_FDG = ['Baseline', 'd1', 'd3', 'd7', 'd14', 'd21', 'd30'] # how the scan times should be named for FDG
OrgTime_UCBH = ['Baseline', 'w1', 'w2', 'w3', 'w4', 'w5', 'w7', 'w9'] # how the scan time should be named for UCBH
StudyGroups = ['mit-lokomotion', 'ohne-lokomotion'] # if there are study groups, if not we can comment it out and exclude it from the script
NewGroups = ['locomotion', 'no-locomotion'] # if there are groups we can save them based on their conditions
DataType = ['DICOM', 'NIFTI'] # type of data
Modality = ['PET', 'CT'] # type of modality
Folder_status = {} # to visually see each folders status
n_sub = 15

# this is a function that copies the files to a new folder
def copy_files(source, destination):
    # Copy all files from the source directory to the destination directory
    for filename in os.listdir(source): # goes into the folder
        source_file = os.path.join(source, filename) # joins the path where the files are and their names
        destination_file = os.path.join(destination, filename) # joins the destination folder for the files are and their names
        if os.path.isfile(source_file): # if there is the source file copies them
            shutil.copytree(source, destination, dirs_exist_ok=True)

# this is a function that counts the number of files in a folder
def files_num(folder_path):
    files = os.listdir(folder_path) # goes into the folder
    files_len = len(files) # counts the number of files
    return files_len # returns the number


# this is a nested for loop that runs through until the number is reached
for l in range(0, 2):  # first loop is for the number of groups for the study groups (conditions) in the project

    for j in range(0, 9):  # the second loop is for the scan time

        for i in range(0, n_sub):  # the first loop is for the number of subjects

            # define wd for Folder1 and Folder2 for FDG and UCBH
            Folder1_FDG = os.path.join(MainFolder, SubFolder, StudyGroups[l], ScanTime_FDG[j], Tracer[0], f'ID{i}',
                                       DataType[0], 'PA1', 'ST1', 'SE1')
            Folder2_FDG = os.path.join(MainFolder, SubFolder, StudyGroups[l], ScanTime_FDG[j], Tracer[0], f'ID{i}',
                                       DataType[0], 'PA1', 'ST1', 'SE2')
            Folder1_UCBH = os.path.join(MainFolder, SubFolder, StudyGroups[l], ScanTime_UCBH[j], Tracer[1], f'ID{i}',
                                        DataType[0], 'PA1', 'ST1', 'SE1')
            Folder2_UCBH = os.path.join(MainFolder, SubFolder, StudyGroups[l], ScanTime_UCBH[j], Tracer[1], f'ID{i}',
                                        DataType[0], 'PA1', 'ST1', 'SE2')

            # here we have different lines for folders based on the tracers included in the project
            Folders = {"Folder1_FDG": Folder1_FDG, "Folder2_FDG": Folder2_FDG, "Folder1_UCBH": Folder1_UCBH,
                       "Folder2_UCBH": Folder2_UCBH}

            # Add a new entry for each ID
            Folder_status[f"ID{i}"] = {"exists": [], "missing": []}
            # Check folder existence of the folders
            for folder_name, folder_path in Folders.items():
                if os.path.exists(folder_path):
                    print(f"{folder_name} exists: {folder_path}")
                    Folder_status[f"ID{i}"]["exists"].append(folder_path)
                else:
                    print(f"{folder_name} does not exist: {folder_path}")
                    Folder_status[f"ID{i}"]["missing"].append(folder_path)

            # check if both SE1 and SE2 folders exist
            if os.path.exists(Folder1_FDG) and os.path.exists(Folder2_FDG):

                # Create working directories to save the data for FDG Tracer
                PET_directory_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                 Tracer[0], OrgTime_FDG[j], DataType[0], Modality[0])
                os.makedirs(PET_directory_FDG, exist_ok=True)
                CT_directory_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                Tracer[0], OrgTime_FDG[j], DataType[0], Modality[1])
                os.makedirs(CT_directory_FDG, exist_ok=True)

                # Count DICOM files in Folder1 for FDG
                Folder1_FDG_len = files_num(Folder1_FDG)
                # Count DICOM files in Folder2
                Folder2_FDG_len = files_num(Folder2_FDG)

                # Copy files based on the conditions for FDG
                if Folder1_FDG_len > Folder2_FDG_len:
                    copy_files(Folder1_FDG, CT_directory_FDG)  # Folder1 to CT_directory
                    copy_files(Folder2_FDG, PET_directory_FDG)  # Folder1 to PET_directory
                else:
                    copy_files(Folder2_FDG, CT_directory_FDG)  # Folder2 to CT_directory
                    copy_files(Folder1_FDG, PET_directory_FDG)  # Folder1 to PET_directory

                # Creat Paths for Converted dicom PET files to nifti
                nii_folder_PET_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                  Tracer[0], OrgTime_FDG[j], DataType[1], Modality[0])
                nii_folder_CT_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                 Tracer[0], OrgTime_FDG[j], DataType[1], Modality[1])
                # create folders
                os.makedirs(nii_folder_PET_FDG, exist_ok=True)
                os.makedirs(nii_folder_CT_FDG, exist_ok=True)

                # Convert dicom to nii
                dicom2nifti.convert_directory(PET_directory_FDG, nii_folder_PET_FDG, compression=False)
                dicom2nifti.convert_directory(CT_directory_FDG, nii_folder_CT_FDG, compression=False)

                # Rename the single NIfTI file for PET FDG
                single_pet_file = os.path.join(nii_folder_PET_FDG, os.listdir(nii_folder_PET_FDG)[0])
                renamed_pet_file = os.path.join(nii_folder_PET_FDG, "FDG_pet.nii")
                os.rename(single_pet_file, renamed_pet_file)
                # CT FDG
                single_pet_file = os.path.join(nii_folder_CT_FDG, os.listdir(nii_folder_CT_FDG)[0])
                print(single_pet_file)
                renamed_pet_file = os.path.join(nii_folder_CT_FDG, "FDG_ct.nii")
                print(renamed_pet_file)
                os.rename(single_pet_file, renamed_pet_file)

            # if only one of the SE1 or SE2 exists save them as PET or CT modality based on their number of dicoms
            elif os.path.exists(Folder1_FDG) or os.path.exists(Folder2_FDG):

                # Copy files based on the conditions for FDG
                if files_num(Folder1_FDG) < 300:
                    PET_directory_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                     Tracer[0], OrgTime_FDG[j], DataType[0], Modality[0])
                    os.makedirs(PET_directory_FDG, exist_ok=True)
                    copy_files(Folder1_FDG, PET_directory_FDG)
                    nii_folder_PET_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                      Tracer[0], OrgTime_FDG[j], DataType[1], Modality[0])
                    os.makedirs(nii_folder_PET_FDG, exist_ok=True)
                    dicom2nifti.convert_directory(PET_directory_FDG, nii_folder_PET_FDG, compression=False)
                    single_pet_file = os.path.join(nii_folder_PET_FDG, os.listdir(nii_folder_PET_FDG)[0])
                    renamed_pet_file = os.path.join(nii_folder_PET_FDG, "FDG_pet.nii")
                    os.rename(single_pet_file, renamed_pet_file)
                elif files_num(Folder2_FDG) < 300:
                    PET_directory_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                     Tracer[0], OrgTime_FDG[j], DataType[0], Modality[0])
                    os.makedirs(PET_directory_FDG, exist_ok=True)
                    copy_files(Folder2_FDG, PET_directory_FDG)  # Folder1 to PET_directory
                    nii_folder_PET_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                      Tracer[0], OrgTime_FDG[j], DataType[1], Modality[0])
                    os.makedirs(nii_folder_PET_FDG, exist_ok=True)
                    dicom2nifti.convert_directory(PET_directory_FDG, nii_folder_PET_FDG, compression=False)
                    single_pet_file = os.path.join(nii_folder_PET_FDG, os.listdir(nii_folder_PET_FDG)[0])
                    renamed_pet_file = os.path.join(nii_folder_PET_FDG, "FDG_pet.nii")
                    os.rename(single_pet_file, renamed_pet_file)
                if files_num(Folder1_FDG) > 300:
                    CT_directory_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                    Tracer[0], OrgTime_FDG[j], DataType[0], Modality[1])
                    os.makedirs(CT_directory_FDG, exist_ok=True)
                    copy_files(Folder1_FDG, CT_directory_FDG)
                    nii_folder_CT_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                     Tracer[0], OrgTime_FDG[j], DataType[1], Modality[1])
                    os.makedirs(nii_folder_CT_FDG, exist_ok=True)
                    dicom2nifti.convert_directory(CT_directory_FDG, nii_folder_CT_FDG, compression=False)
                    single_pet_file = os.path.join(nii_folder_CT_FDG, os.listdir(nii_folder_CT_FDG)[0])
                    renamed_pet_file = os.path.join(nii_folder_CT_FDG, "FDG_ct.nii")
                    os.rename(single_pet_file, renamed_pet_file)
                elif files_num(Folder2_FDG) > 300:
                    CT_directory_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                    Tracer[0], OrgTime_FDG[j], DataType[0], Modality[1])
                    os.makedirs(CT_directory_FDG, exist_ok=True)
                    copy_files(Folder2_FDG, CT_directory_FDG)
                    nii_folder_CT_FDG = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                     Tracer[0], OrgTime_FDG[j], DataType[1], Modality[1])
                    os.makedirs(nii_folder_CT_FDG, exist_ok=True)
                    dicom2nifti.convert_directory(CT_directory_FDG, nii_folder_CT_FDG, compression=False)
                    single_pet_file = os.path.join(nii_folder_CT_FDG, os.listdir(nii_folder_CT_FDG)[0])
                    renamed_pet_file = os.path.join(nii_folder_CT_FDG, "FDG_ct.nii")
                    os.rename(single_pet_file, renamed_pet_file)
            ##################################################### UCBH Tracer ###################################################
            if os.path.exists(Folder1_UCBH) and os.path.exists(Folder2_UCBH):

                CT_directory_UCBH = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                 Tracer[1], OrgTime_UCBH[j], DataType[0], Modality[1])
                os.makedirs(CT_directory_UCBH, exist_ok=True)
                PET_directory_UCBH = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                  Tracer[1], OrgTime_UCBH[j], DataType[0], Modality[0])
                os.makedirs(PET_directory_UCBH, exist_ok=True)

                # Count DICOM files in Folder1 for UCBH
                Folder1_UCBH_len = files_num(Folder1_UCBH)
                # Count DICOM files in Folder2
                Folder2_UCBH_len = files_num(Folder2_UCBH)

                # Copy files based on the conditions for UCBH
                if Folder1_UCBH_len > Folder2_UCBH_len:
                    copy_files(Folder1_UCBH, CT_directory_UCBH)  # Folder1 to CT_directory
                    copy_files(Folder2_UCBH, PET_directory_UCBH)  # Folder2 to PET_directory
                else:
                    copy_files(Folder2_UCBH, CT_directory_UCBH)  # Folder2 to CT_directory
                    copy_files(Folder1_UCBH, PET_directory_UCBH)  # Folder1 to PET_directory

                # Convert dicom PET files to nifti
                nii_folder_PET_UCBH = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                   Tracer[1], OrgTime_UCBH[j], DataType[1], Modality[0])
                nii_folder_CT_UCBH = os.path.join(MainFolder, OutputFolder, SubOutputFolder, NewGroups[l], f'ID{i}',
                                                  Tracer[1], OrgTime_UCBH[j], DataType[1], Modality[1])
                os.makedirs(nii_folder_PET_UCBH, exist_ok=True)
                os.makedirs(nii_folder_CT_UCBH, exist_ok=True)

                # Convert dicom to nii
                dicom2nifti.convert_directory(PET_directory_UCBH, nii_folder_PET_UCBH, compression=False)
                dicom2nifti.convert_directory(CT_directory_UCBH, nii_folder_CT_UCBH, compression=False)

                # PET UCBH
                single_pet_file = os.path.join(nii_folder_PET_UCBH, os.listdir(nii_folder_PET_UCBH)[0])
                renamed_pet_file = os.path.join(nii_folder_PET_UCBH, "UCBH_pet.nii")
                os.rename(single_pet_file, renamed_pet_file)

                # CT UCBH
                single_pet_file = os.path.join(nii_folder_CT_UCBH, os.listdir(nii_folder_CT_UCBH)[0])
                renamed_pet_file = os.path.join(nii_folder_CT_UCBH, "UCBH_ct.nii")
                os.rename(single_pet_file, renamed_pet_file)
