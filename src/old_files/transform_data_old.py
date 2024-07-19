'''
Class for connecting to google sheets api and update db.

Started: 6/15/2023
Last Updated: 6/15/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################
import requests
import sqlite3
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import create_engine, exc

# DB manager class for composition
from methane_project.src.old_files.db_manager_class import MethaneDB
from methane_project.src.fetch_data_from_api import FetchData


#####################################################################################################################
## CLASS
#####################################################################################################################

class TransformData():
    def __init__(self, df: pd.DataFrame, database):
        self.df = df
        self.db = database

    def get_lat_and_long(self):

        try:
            # seperate coordinates col into lat and long, then drop coordinates
            self.df[['latitude', 'longitude']] = self.df.loc[:, 'coordinates'].str.split(",", expand=True)
            self.df = self.df.drop(columns='coordinates', inplace=True)

        except Exception as e:
            print(f"Failed to get latittude and longitude. {e}")

    def get_images(self):

        try:
            ## download photos and add to photo table, replace photo in df with photo_id
            id_list = []
            for idx, link in self.df['photo'].items():
                if link:
                    print(link)
                    image = self.download_image_from_drive(link)
                    image_id = self.db.add_image(idx, image)
                    id_list.append(image_id)
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

    def get_volunteer_id(self):
        # get volunteer id
        pass

    def download_image_from_drive(self, drive_link):
        '''
        Get image links and download from google drive.
        '''
        try:
            # Convert Google Drive link to direct download link
            file_id = drive_link.split('=')[1]
            print(f"file_id: {file_id}")
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            # download image data
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                # Read the image data into memory
                image_data = response.content
                print('Image data downloaded succesfully.')
                return image_data
            else:
                print(f"Failed to download image. HTTP Status Code: {response.status_code}")
                return None
            
        except requests.RequestException as e:
            print(f"Failed to download image. Network error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    
    def execute(self):
        '''
        Updates DB from Google Sheet API
        '''
        try:
            self.get_lat_and_long()
            self.get_images()
            self.get_leaks()
            
            print('Data formated successfully')
            print(self.df)
            return self.df
            
        except Exception as e:
            print(f"Execution failed: {e}")
            raise

#####################################################################################################################
## DRIVER
#####################################################################################################################
if __name__ == '__main__':

    credentials_path = 'credentials.json'
    GOOGLE_SHEET_ID = '1oJ2wAGYLkEd8VeKinrbiAmOwjlZpYqONL09P4LZ01po'
    RANGE_NAME = 'Form Responses 1!A1:G'
    
    google_sheets_to_sql = FetchData(credentials_path, GOOGLE_SHEET_ID, RANGE_NAME)
    df = google_sheets_to_sql.execute()

    format_data_for_Sql = TransformData(df)
    format_data_for_Sql.execute()

#####################################################################################################################
## END
#####################################################################################################################