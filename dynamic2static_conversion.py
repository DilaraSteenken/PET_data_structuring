######################### dynamic image to static image conversion ###########################################
# in this script we export the data frames containing the last 30 mins uptake values and convert them to static images

# import packages
import numpy as np
import os
import nibabel as nib
import numpy as np
import json
from pathlib import Path
import yaml

# loading working directory
project_dir = Path(r"C:\Users\dsteenke\PycharmProjects\data_structuring")
config_path = project_dir / "config.local.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
settings = config["dynamic_2_static"]
# defining paths
MainFolder = settings["MainFolder"]
SubFolder = settings["SubFolder"]
StudyConditions = settings["StudyConditions"]


DataType = ['NIFTI']
Modality = 'PET' # type of modality
Tracers = ['UCBH'] # type of tracer
n = 25 # number of subjects

# Loop through subjects
for i in range(1, n):
    for tracer in Tracers:
        # wdir for scan time
        scan_time_dir = os.path.join(MainFolder, SubFolder, f'ID{i}', tracer)
        # check if wdir exists
        if not os.path.exists(scan_time_dir):
            print(f"Scan time folder does not exist: {scan_time_dir}")
            continue
        # if exists, list them by looking into the folder
        scan_times = os.listdir(scan_time_dir)

        # loop through scan times
        for time in scan_times:

            # wdir for study conditions
            condition_dir = os.path.join(scan_time_dir, time)
            if not os.path.isdir(condition_dir):
                continue

            # if condition exists, list the conditions
            items_in_condition_dir = os.listdir(condition_dir)

            # define study conditions. If there are more conditions, add them to the list above, and add more if-else statements
            condition = StudyConditions[0] if StudyConditions[0] in items_in_condition_dir else StudyConditions[1]

            # define the wd for nifti folder
            nifti_folder = os.path.join(condition_dir, condition, 'NIFTI', Modality)

            # if nifti folder does not exist continue
            if not os.path.exists(nifti_folder):
                print(f"Folder does not exist: {nifti_folder}")
                continue
            else:
                print(f"Folder exists: {nifti_folder}")

            # once the nifti folders are defined, loop through them
            for file in os.listdir(nifti_folder):
                # check if file ends with nii
                if file.endswith('.nii.gz'): # potentially could add "or file.endswith('.nii'):
                    dynamic_file = os.path.join(nifti_folder, file)
                    json_file = dynamic_file.replace('.nii.gz', '.json') # define .json file

                    # Load NIfTI file
                    img = nib.load(dynamic_file) # load image
                    data = img.get_fdata() # data
                    hdr = img.header # hdr

                    # Check 4D
                    if data.ndim != 4:
                        print(f"Skipping non-4D image: {dynamic_file}")
                        continue

                    # Load timing from .json
                    if not os.path.exists(json_file):
                        print(f"Missing JSON file: {json_file}")
                        continue
                    # open metadata for the timing
                    with open(json_file, 'r') as f:
                        metadata = json.load(f)

                    # extract start time and durations
                    try:
                        start_times = metadata['FrameTimesStart']
                        durations = metadata['FrameDuration']

                    except KeyError:
                        print(f"Missing timing info in JSON: {json_file}")
                        continue

                    # Check for frames
                    frame_n = 23 # define frames
                    if len(start_times) < frame_n or data.shape[3] < frame_n:
                        print(f"Not enough frames in {dynamic_file}")
                        continue

                    # Frame indices 21–23 (0-based: 20–22)
                    frame_indices = [20, 21, 22]
                    print(f"\nSubject ID{i}, Tracer {tracer}, Time {time}")

                    # loop through frame indices
                    for idx in frame_indices:
                        start = start_times[idx]
                        duration = durations[idx]
                        end = start + duration
                        print(f"Frame {idx+1}: Start = {start:.2f}s, End = {end:.2f}s, Duration = {duration:.2f}s")

                    # Average the selected frames
                    frames_to_average = data[..., frame_indices]
                    averaged_data = np.mean(frames_to_average, axis=-1)

                    # Save new static image
                    output_name = f'ID{i}_{tracer}_{time}_avg_21_23.nii.gz'
                    output_path = os.path.join(nifti_folder, output_name)
                    static_img = nib.Nifti1Image(averaged_data, affine=img.affine, header=hdr)
                    nib.save(static_img, output_path)
                    print(f"Saved: {output_path}")