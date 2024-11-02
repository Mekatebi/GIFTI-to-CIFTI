# ROI Converter: GIFTI to CIFTI

A Python script for converting GIFTI ROI files to CIFTI dense scalar format.

## Description
This script converts `.func.gii` files to `.dscalar.nii` format, processing all GIFTI files in the specified input directory.

## Features
* Converts GIFTI ROI files to CIFTI format
* Creates dense CIFTI files using wb_command
* Handles both left and right hemisphere ROIs
* Batch processing

## Requirements
* nibabel
* numpy
* Connectome Workbench (wb_command)

## Setup
Configure the following paths in the script:
```
CIFTI_TEMPLATE = "path/to/template.dscalar.nii"
INPUT_FOLDER_PATH = "path/to/input/folder"
OUTPUT_FOLDER_PATH = "path/to/output/folder"
WB_COMMAND = "path/to/wb_command.exe"
```

## Usage
1. Place `.func.gii` files in the input folder
2. Run the script:
```
python ROI_Converter.py
```
3. Find converted files in the output folder

## Notes
* Input filenames must contain "LEFT" or "RIGHT" to indicate hemisphere
* Creates both standard and dense CIFTI files
* Processes all `.func.gii` files in input directory
