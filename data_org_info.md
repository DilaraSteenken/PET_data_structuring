# explanation for the codes
# dcm2nii: the first goal is to define the PET and CT dicoms based on the number of files and rename the folders while converting them to nifti
# BIDS_formating: in this script we then organise the data structure and rename the PET/CT files in a BIDS-compatible way (not fully though)
# Scan_info_df: here we create a data frame including each project and study information to use during preprocessinf
# data_org_bids_format: this is a combined version of dcm2nii, BIDS_formating, and Scan_info_df 
# dynamic2static_conversion: if .nii and .json files exist, converting to static images 
#* our BIDS-formating does not include .json files, which would need to be updated
