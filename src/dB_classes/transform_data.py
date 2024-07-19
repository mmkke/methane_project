'''
Class for connecting to google sheets api and update db.

Started: 6/15/2023
Last Updated: 7/6/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################
import requests
import sqlite3
import pandas as pd
import numpy as np
import re

#####################################################################################################################
## LIBRARIES
#####################################################################################################################
from image_wrangler import ImageWrangler

#####################################################################################################################
## CLASS
#####################################################################################################################
class TransformData():
    def __init__(self, path_to_db):
        self.df = None
        self.path_to_db = path_to_db
        self.image_wrangler = ImageWrangler(path_to_db)
    
    def set_df(self, df):
        self.df = df
    
    def get_df(self):
        return self.df

    def get_lat_and_long(self):

        try:
            # Check for valid coordinates using regex and create mask
            valid_mask = self.df['coordinates'].apply(lambda x: self.is_valid_coord(x))
            print(valid_mask)

            # Where coordinates are valid, remove parentheses and separate coordinates col into lat and long
            self.df[['latitude', 'longitude']] = (
                self.df['coordinates'].where(valid_mask)
                    .str.replace(r"[()]", "", regex=True)
                    .str.split(",", expand=True)
            )
            
            # Convert latitude and longitude to float
            self.df['latitude'] = self.df['latitude'].astype(float)
            self.df['longitude'] = self.df['longitude'].astype(float)

            # Where coordinates are not valid, set latitude and longitude to NaN
            self.df.loc[~valid_mask, ['latitude', 'longitude']] = np.nan

            # Drop the original coordinates column
            self.df.drop(columns=['coordinates'], inplace=True)

        except Exception as e:
            print(f"Failed to get latittude and longitude. {e}")
    
    def is_valid_coord(self, s):

        # Define the pattern for a valid coordinate
        pattern = r'^\s*\(?\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\)?\s*$'
    
        # Use re.match to check if the string matches the pattern
        return bool(re.match(pattern, s))

    def get_images(self):

        try:
            ## download photos and add to photo table, replace photo in df with photo_id
            id_list = []
            for idx, link in self.df['photo'].items():
                if link:
                    print(f"\nDownloading image from {link}")
                    photo_id = self.image_wrangler.execute(link)
                    id_list.append(photo_id)
                else:
                    id_list.append(None)
            self.df['photo_id'] = pd.Series(id_list)
            self.df.drop(columns='photo', inplace=True)

        except Exception as e:
            print(f"Failed to get images. {e}")
    
    def get_leaks(self):
        try:
            ## add leak col (if methane_level > 0 then True)
            self.df['leak'] = np.where(self.df['methane_level'].astype(float) > 0, True, False)

        except Exception as e:
            print(f"Failed to get leak. {e}")     

    def get_volunteers(self):
        try:
            # Make capitals
            self.df['volunteer'] = self.df['volunteer'].str.upper()
        except Exception as e:
            print(f"Failed to format volunteer initials. {e}")
    
    def format_timestamp(self):

        # Convert to ISO 8601 format
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], 
                                              format='%m/%d/%Y %H:%M:%S', 
                                              errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

    def lel_to_ppm(self):
        # Convert Lower Explosive Limit (lel) to Parts per Million (ppm)

        self.df['methane_level'] = self.df['methane_level'].apply(lambda x: float(x) * 50000 * 0.01)

    def execute(self, df):
        '''
        Updates DB from Google Sheet API
        '''
        try:
            self.set_df(df)
            self.format_timestamp()
            self.get_lat_and_long()
            self.get_images()
            self.get_leaks()
            self.lel_to_ppm()
            self.get_volunteers()
            
            print('Data formated.')
            print(self.df)
            return self.df
            
        except Exception as e:
            print(f"Execution failed: {e}")
            raise

#####################################################################################################################
## END
#####################################################################################################################