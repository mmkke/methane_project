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


#####################################################################################################################
## CLASS
#####################################################################################################################

class GoogleSheetsToSQL():
    def __init__(self, credentials_path, sheet_id, range_name, db_connection_string):
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.range_name = range_name
        self.db_connection_string = db_connection_string
        self.service = self.init_google_sheets_api()
        self.df = None
        self.df_formated = None
        self.MethaneDB = MethaneDB('methane_project_DB')

    def init_google_sheets_api(self):
        '''
        Connects to Google Sheet API
        '''
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        try:
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
            service = build('sheets', 'v4', credentials=creds)
            return service
        except Exception as e:
            print(f"Failed to initialize Google Sheets API: ", e)
            raise

    def read_sheet(self):
        '''
        Reads Google Sheet and assigns to self.df.
        '''
        try:
            sheet = self.service.spreadsheets().values().get(spreadsheetId=self.sheet_id, range=self.range_name).execute()
            data = sheet.get('values', [])
            if not data:
                raise ValueError("No data found in the specified range.")
            
            headers = data.pop(0)  # Assume the first row is the header
            self.df = pd.DataFrame(data, columns=headers)
            print("Data successfully read from Google Sheet.")
            print(self.df)
            return self.df
        except Exception as e:
            print(f"Failed to read data from Google Sheets: ", e)
            raise

    def connect_to_db(self):
        '''
        Creates database connection.
        '''
        try:
            engine = create_engine(self.db_connection_string)
            print('Connected to DB.')
            return engine
        except Exception as e:
            print("Recieved the following error when attempting to connect to DB: ", e)
            raise
        

    def insert_data_to_sql(self, table_name):
        '''
        Adds df_formated to sql.
        '''
        try:
            # format df to match measurements table
            self.format_sheet_data_for_DB()

            # open db connection
            self.MethaneDB.connect()

            # insert data
            self.df_formated.to_sql(table_name, con=self.MethaneDB.connection, if_exists='append', index=False)
            print("Data inserted successfully")

        except Exception as e:
            print(f"Failed to insert data into the SQL table: {e}")
            raise
        finally:
            if self.MethaneDB.connection:
                self.MethaneDB.connection.close()
    
    def format_sheet_data_for_DB(self):
        '''
        Formats dataframe to match measurments table.
        '''
        df = self.df

        # seperate coordinates col into lat and long, then drop coordinates
        df[['latitude', 'longitude']] = df.loc[:, 'coordinates'].str.split(",", expand=True)
        df.drop(columns='coordinates', inplace=True)

        ## download photos and add to photo table, replace photo in df with photo_id
        id_list = []
        for idx, link in df['photo'].items():
            if link:
                print(link)
                image = self.download_image_from_drive(link)
                image_id = self.insert_image_to_db(idx, image)
                id_list.append(image_id)
            else:
                id_list.append(None)
        df['photo_id'] = pd.Series(id_list)
        df.drop(columns='photo', inplace=True)

        ## add leak col (if methane_level > 0 then True)
        df['leak'] = np.where(df['methane_level'].astype(float) > 0, True, False)

        # get volunteer id
        pass

        self.df_formated = df
        print('Data formated successfully')
        print(self.df_formated)

    def download_image_from_drive(self, drive_link):
        '''
        Get image links and download from google drive.
        '''
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
    
    def insert_image_to_db(self, idx, image_data):
        '''
        Add image to photo table.
        '''
        #conn = sqlite3.connect("mydatabase.db")
        #cur = conn.cursor()
        self.MethaneDB.connect()

        
        # Create table if it doesn't exist
        self.MethaneDB.cur.execute('''
                    CREATE TABLE IF NOT EXISTS photos(
                        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        photo BLOB,
                        hash TEXT UNIQUE
                        )
                    ''')
        
        # Insert the image as a BLOB with the unique ID
        self.MethaneDB.cur.execute('''
            INSERT INTO photos (photo, hash) VALUES (?, ?)
        ''', (image_data, idx))

        # Get the primary key of the last inserted row
        photo_id = self.MethaneDB.cur.lastrowid
        
        self.MethaneDB.connection.commit()
        self.MethaneDB.connection.close()
        print(f"Image inserted into the database with photo_id: {photo_id}")

        return photo_id

    def execute(self, table_name):
        '''
        Updates DB from Google Sheet API
        '''
        try:
            df = self.read_sheet()
            self.insert_data_to_sql(table_name)
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
    DB_CONNECTION_STRING = 'sqlite:///mydatabase.db'
    TABLE_NAME = 'measurements'
    
    google_sheets_to_sql = GoogleSheetsToSQL(credentials_path, GOOGLE_SHEET_ID, RANGE_NAME, DB_CONNECTION_STRING)
    google_sheets_to_sql.execute(TABLE_NAME)

#####################################################################################################################
## END
#####################################################################################################################