#!/usr/bin/env python3
"""
ROI Converter: GIFTI to CIFTI

This script converts GIFTI ROI files (.func.gii) to CIFTI dense scalar files (.dscalar.nii).
It processes all .func.gii files in the input directory and creates corresponding CIFTI files.

Features:
- Converts GIFTI ROI files to CIFTI format
- Creates dense CIFTI files using wb_command
- Handles both left and right hemisphere ROIs (must be specified in the filename)

Requirements:
- nibabel
- numpy
- Connectome Workbench (wb_command)

Author: Mohammad Ebrahim Katebi
"""

import os
import subprocess
from typing import List, Tuple

import nibabel as nb
import numpy as np
from nibabel import cifti2

# Configuration Constants
CIFTI_TEMPLATE = "./S1200_7T_Retinotopy181.Fit1_Eccentricity_MSMAll.32k_fs_LR.dscalar.nii"
INPUT_FOLDER_PATH = "./"
OUTPUT_FOLDER_PATH = "./"
WB_COMMAND = "E:/Applications/HCP_Workbench/bin_windows64/wb_command.exe"
DENSE_TEMPLATE = CIFTI_TEMPLATE


def run_wb_command(input_file: str) -> None:
    """
    Run wb_command to create dense CIFTI file.

    Args:
        input_file (str): Path to input CIFTI file

    Raises:
        subprocess.CalledProcessError: If wb_command execution fails
    """
    input_path = os.path.abspath(input_file)
    output_path = input_path.replace('.dscalar.nii', '_Full.dscalar.nii')

    command = [
        WB_COMMAND,
        '-cifti-create-dense-from-template',
        DENSE_TEMPLATE,
        output_path,
        '-cifti',
        input_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully ran wb_command on {os.path.basename(input_file)}")
    except subprocess.CalledProcessError as e:
        print(
            f"Error running wb_command on {os.path.basename(input_file)}: {str(e)}")


def process_roi(roi_path: str) -> None:
    """
    Process a single ROI file and convert it to CIFTI format.

    Args:
        roi_path (str): Path to input GIFTI ROI file

    Raises:
        ValueError: If hemisphere cannot be determined from filename
        Exception: For any other processing errors
    """
    # Determine hemisphere from filename
    filename = os.path.basename(roi_path)
    if 'RIGHT' in filename.upper():
        hemi = 'R'
    elif 'LEFT' in filename.upper():
        hemi = 'L'
    else:
        raise ValueError(f"Cannot determine hemisphere for file: {filename}")

    # Load and process data
    img = nb.load(roi_path)
    img_data = [x.data for x in img.darrays]
    cur_data = np.reshape(img_data, (len(img_data[0]), len(img_data)))

    # Load CIFTI template and setup
    cifti = nb.load(CIFTI_TEMPLATE)
    cifti_hdr = cifti.header
    axes = [cifti_hdr.get_axis(i) for i in range(cifti.ndim)]
    brain_model_axis = axes[1]

    # Process CIFTI indices
    cifti_indices_to_gifti_vertices = brain_model_axis.vertex
    cifti_indices_to_gifti_vertices = np.vstack((
        np.arange(cifti_indices_to_gifti_vertices.shape[0]),
        cifti_indices_to_gifti_vertices
    )).T

    # Select hemisphere structure
    structure_name = ('CIFTI_STRUCTURE_CORTEX_RIGHT' if hemi == 'R'
                      else 'CIFTI_STRUCTURE_CORTEX_LEFT')

    cifti_surf_brain_model_axis = brain_model_axis[
        (brain_model_axis.name == structure_name)
    ]
    result_brain_model_axis = brain_model_axis[
        (brain_model_axis.name == structure_name)
    ]

    # Create result data
    cifti_surf_indices_to_gifti_vertices = cifti_surf_brain_model_axis.vertex[:, np.newaxis]
    roi_gifti_vertices = np.where(cur_data == 1)[0]
    roi_cifti_indices = np.flatnonzero(
        np.isin(cifti_surf_indices_to_gifti_vertices[:, 0], roi_gifti_vertices)
    )

    result_cifti_data = np.zeros(result_brain_model_axis.vertex.shape[0])[
        np.newaxis, :]
    result_cifti_data[0, roi_cifti_indices] = 1

    # Save results
    result_cifti_header = cifti2.Cifti2Header.from_axes((
        cifti2.ScalarAxis(['ROI_Mask']),
        result_brain_model_axis
    ))

    output_roi_mask_filename = filename.replace('.func.gii', '.dscalar.nii')
    output_roi_mask_filepath = os.path.join(
        OUTPUT_FOLDER_PATH, output_roi_mask_filename)

    result_img = nb.Cifti2Image(result_cifti_data, header=result_cifti_header)
    result_img.to_filename(output_roi_mask_filepath)
    print(f"Processed: {filename}")

    # Create dense CIFTI file
    run_wb_command(output_roi_mask_filepath)


def main() -> None:
    """
    Main function to process all ROI files in the input directory.
    
    Creates output directory if it doesn't exist and processes all .func.gii files.
    """
    if not os.path.exists(OUTPUT_FOLDER_PATH):
        os.makedirs(OUTPUT_FOLDER_PATH)

    for filename in os.listdir(INPUT_FOLDER_PATH):
        if filename.endswith('.func.gii'):
            roi_path = os.path.join(INPUT_FOLDER_PATH, filename)
            try:
                process_roi(roi_path)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    main()
