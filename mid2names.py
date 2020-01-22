"""Create LUT from a given db

Script to create a LUT table with FID.MID as the keys and English names as values. The script assumes the file structure
to be F0001/MID1 for all FIDs. It then reads all the mid.csv files in the MID? folders and append them to a dataframe.

The purpose of this script is to prepare FIW for finding overlapping names across other datasets.
"""

import glob
import re
from tqdm import tqdm
import pandas as pd


def clean_name(name):
    """ Cleans a given input name.

	Args:
		name: input name

	Returns:
		cleaned name
	"""
    # TODO: implement this method
    pass


def import_fiw_names(path):
    """ Create a LUT from all the names of the db

	Args:
		path: Path to the folder containing FIDs

	Returns:
		Saves a file with the name FIW_LUT.csv.
		Returns dataframe of FIW_LUT
	"""
    # make sure the path ends with a '/'
    if not re.search(r'\/$', path):
        path += '/'

    # read all the paths matching the given format
    paths = sorted(glob.glob(path + 'F????/mid.csv'))

    df = pd.DataFrame(
        columns=['source_db', 'fid', 'mid', 'gender', 'first', 'first_alias', 'last', 'last_alias', 'name'])

    # Read a csv file which contains last names of all the FIDs
    last_name_file_path = '/'.join(path.split('/')[:-2]) + '/FIW_FIDs.csv'
    last_name_df = pd.read_csv(last_name_file_path)

    for p in tqdm(paths):
        # Extract fid from path
        fid = re.sub(r'.*(F\d{4}).*', r'\1', p)

        d = pd.read_csv(p)

        # this check is applied because a few families are missing in last_name_df. it will be fixed in future
        if fid in last_name_df['fid'].values:
            last = last_name_df.query('fid==@fid').iloc[0]['surname'].split('.')[0]
        else:
            last = ''

        # TODO: Develop a way to get aliases

        for i in d.index:
            first, mid, gender = d.loc[i, ['Name', 'MID', 'Gender']]
            first_alias = ''  # alias
            last_alias = ''  # to be fetched
            name = ' '.join([first, last]).strip()
            df.loc[len(df)] = ['FIW', fid, mid, gender, first, first_alias, last, last_alias, name.lower()]

    df.to_csv('FIW_LUT.csv', index=False)
    return df


def import_family101_names(path):
    """Create a LUT for Family101 db

    Args:
        path: path to the FAMILY101.txt file

    Returns:
        Saves a file with the name Family101_LUT.csv.
        returns a dataframe with all the names from family101 db
    """
    # open the file containing family101 names
    f = open(path)

    df = pd.DataFrame(columns=['source_db', 'name', 'gender', 'relation', 'first', 'last', 'family_name'])
    
    for row in tqdm(f.readlines()):
        row = re.sub(r'\n', '', row)
        if row:

            # Each row has a structure "1   HUSB    Barac_Obama"
            row_split = row.split()
            relation, name = row_split[1], row_split[2].replace('_', ' ')

            # These rows are not of any use, they just mention the family surname
            if relation == 'FAMI':
                family_name = name
            else:
                name_split = name.split()
                first, last = '', ''
                if len(name_split) > 1:
                    first, last = name_split[0], name_split[-1]

                # There are only 4 relations ["HUSB", "WIFE", "SONN", "DAUG"]
                if relation == 'HUSB' or relation == 'SONN':
                    gender = 'm'
                else:
                    gender = 'f'

                df.loc[len(df)] = 'family101', name.lower(), gender, relation, first, last, family_name
    df.to_csv('Family101_LUT.csv', index=False)
    return df


# Testing code
import sys

if __name__ == "__main__":
    p = sys.argv[1]
    import_fiw_names(p)
    import_family101_names(p)
