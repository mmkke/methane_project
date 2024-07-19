'''
Class for connecting to google sheets api and update db.

Started: 6/15/2023
Last Updated: 7/6/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################

import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

#####################################################################################################################
## CLASS
#####################################################################################################################

class FetchData():
    def __init__(self, credentials_path, sheet_id, range_name):
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.range_name = range_name
        self.service = self.init_google_sheets_api()
        self.df = None

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

        except Exception as e:
            print(f"Failed to read data from Google Sheets: ", e)
            raise

    def to_csv(self):
        '''
        Exports raw data to csv.
        '''
        try:
            # get time
            now = datetime.utcnow()

            # Format the time as year:month:day:hour:minute:second
            timestamp = now.strftime("%Y:%m:%d:%H:%M:%S")

            # Export raw data to csv
            self.df.to_csv(f'data/api_data/raw_{timestamp}.csv', index=False)

        except Exception as e:
            print(f"Failed to write data: ", e)
            raise

    def execute(self):
        '''
        Updates DB from Google Sheet API
        '''
        try:
            self.read_sheet()
            self.to_csv()
            return self.df
        
        except Exception as e:
            print(f"Execution failed: {e}")
            raise


#####################################################################################################################
## END
#####################################################################################################################