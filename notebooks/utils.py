import os
import numpy as np 
import pandas as pd

def transform_fcsv(input_fcsv, output_fcsv, transform, invert=0):
    '''Applies ANTs transform to 3D slicer fcsv file in 3 steps:
        
    1. Slicer fcsv (RAS) is converted to ANTs-compatible (LPS) csv
    2. The transform is applied to the csv via antsApplyTransformsToPoints
    3. The transformed csv is converted back to Slicer fcsv format
    Function is based on afids-tools legacy scripts github.com/afids/afids-tools

    Parameters
    ----------
    input fcsv: path to input Slicer fcsv file
    ouput fcsv: path to output Slicer fcsv file
    transform: path to ANTs transform file (either linear .mat or .nii.gz warp)
    invert: if 1, linear .mat is inverted. This option doesn't work for warps.
            Instead use the inverse warp (given by ANTs) as input
    '''

    # get output directory
    output_dir = os.path.dirname(output_fcsv)
    # temporary csv files are also saved in the same output directory
    orig_csv = os.path.join(output_dir, 'tmp_orig.csv')
    transformed_csv = os.path.join(output_dir, 'tmp_transformed.csv')

    # convert Slicer RAS oriented FCSV (default)
    # to Ants LPS oriented format (expected orientation)
    # use with CAUTION: orientation flips here
    df = pd.read_csv(input_fcsv, skiprows=2)
    coords = df.loc[:, ['x', 'y', 'z']]
    coords['t'] = np.zeros(len(coords)) # add a 4th dimension of zeros 
    coords['x'] = -1 * coords['x'] # flip orientation in x
    coords['y'] = -1 * coords['y'] # flip orientation in y
    coords.to_csv(orig_csv, index=False, float_format='%.3f')

    # apply transforms to original csv and get transformed csv
    cmd1 = f'antsApplyTransformsToPoints -d 3 -i {orig_csv} -o {transformed_csv}'
    cmd2 = f' -t [{transform}, {invert}]'
    os.system(cmd1 + cmd2)

    new_coords = pd.read_csv(transformed_csv)
    # flip x and y signs, to convert back from ANTs LPS to slicer RAS space
    df['x'] = -1 * new_coords['x'].values.round(3)
    df['y'] = -1 * new_coords['y'].values.round(3)
    df['z'] = new_coords['z'].values.round(3)

    # read lines from input_fcsv
    with open(input_fcsv, 'r') as file:
        lines = file.readlines()
    # replace data lines (leave header unchanged)
    for i in df.index:
        row_entries = [str(cell) for cell in df.iloc[i, :].values]
        lines[3 + i] = ','.join(row_entries) + '\n'
    # write lines to outout_fcsv
    with open(output_fcsv, 'w') as file:
        file.writelines(lines)

    # remove temporary files
    os.remove(orig_csv)
    os.remove(transformed_csv)
    