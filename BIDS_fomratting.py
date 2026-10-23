###################################### BIDS format ###################################################################
# in this script we rename the pet and ct files ina BIDS-compatible way

# import packages
import os
import re
import nibabel as nib
from pathlib import Path
import yaml

# loading paths from ymal file
project_dir = Path(r"C:\Users\dsteenke\PycharmProjects\data_structuring")
config_path = project_dir / "config.local.yaml"
with open(config_path, "r", encoding="utf-8") as f: # reading file
    config = yaml.safe_load(f)
settings = config["bids_conversion"]
# defining paths
main_folder = settings["main_folder"]
sub_folder = settings["sub_folder"]
project_folder = settings["project_folder"]
output = settings["output"]

# Variables
modalities = ['PET', 'CT']
tracers = ['FDG', 'UCBH']
output_main_dir = 'raw'
proj = 'bUVN'

# Compose path to input data
input_path = os.path.join(main_folder, sub_folder, project_folder)
# get a list for all subjects
all_subjects = os.listdir(input_path)

# loop through subjects
for subj in all_subjects:

    # Extract subject number from folder name like 'ID123'
    match = re.search(r'\d+', subj)
    if not match:
        print(f"Could not extract number from subject: {subj}")
        continue

    # define subject id
    subject_num = match.group().zfill(2)  # zero-padded
    sub_id = f"sub-{subject_num}"

    for tracer in tracers:
        # define scan time folder
        scan_time_dir = os.path.join(input_path, subj, tracer)

        if not os.path.exists(scan_time_dir):
            print(f"Missing tracer directory: {scan_time_dir}")
            continue

        scan_times = os.listdir(scan_time_dir)
        # loop through follow-up scans
        for time in scan_times:
            # session name is BIDS compatible
            session = f"ses-{str(time)}"

            # define condition
            time_folder = os.path.join(scan_time_dir, time)
            if not os.path.exists(time_folder):
                continue
            # always only one condition folder and select that one for file naming
            conditions = os.listdir(time_folder)
            if not conditions:
                print(f"No condition folder found: {time_folder}")
                continue
            else:
                condition = conditions[0]

            for modality in modalities:
                nifti_folder = os.path.join(scan_time_dir, time, condition, 'NIFTI', modality)
                if not os.path.exists(nifti_folder):
                    print(f"NIfTI folder missing: {nifti_folder}")
                    continue

                # filename based on organised but not bids format
                if modality == 'PET':
                    filename = f'{tracer}_pet.nii'
                else:
                    filename = f'{tracer}_ct.nii'

                # define scan filename
                scan_file = os.path.join(nifti_folder, filename)
                if not os.path.isfile(scan_file):
                    print(f"Scan file not found: {scan_file}")
                    continue

                # Construct output BIDS directory and filename
                bids_dir = os.path.join(main_folder, output_main_dir, output, sub_id, session, modality.lower())
                os.makedirs(bids_dir, exist_ok=True)

                bids_name = f"{sub_id}_{session}_trc-{tracer.lower()}_{proj}_{condition}_rec-stat_{modality.lower()}.nii.gz"
                output_file = os.path.join(bids_dir, bids_name)

                try:
                    # Load and save compressed .nii.gz
                    img = nib.load(scan_file)
                    nib.save(img, output_file)
                    print(f"Saved: {output_file}")
                except Exception as e:
                    print(f"Failed to process {scan_file}: {e}")