# PET_data_structuring
- The dcm2nii is the first script used to convert the data define PET and CT folders and organise them in a consistent way. 
- After dcm2nii, we used the BIDS_formating to rename each file accordingly and structure the folders BIDS-like.
- Then, we used the Scan_info_df to create an excel sheet that includes all subject, project, modality and scan times.
- data-org-bids-format is a combined script of folder structuring, BIDS naiming and data table creation. 
- dynamic2static is to convert the last 30 mins to static scans by averaging the time frames. 
- the scripts would need to be adjusted on needs as they are specific to our data. 
- the config.example.yaml is to define the working directories and study conditions for each script. 
