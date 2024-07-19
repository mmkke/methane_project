
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import create_engine

# Initialize the Google Sheets API
def init_google_sheets_api():
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    PATH_TO_CREDENTIALS = 'credentials.json'
    creds = Credentials.from_service_account_file(PATH_TO_CREDENTIALS, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)
    return service

# Read data from Google Sheets
def read_sheet(sheet_id, range_name):
    service = init_google_sheets_api()
    sheet = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    data = sheet.get('values', [])
    headers = data.pop(0)  # Assume the first row is the header
    return pd.DataFrame(data, columns=headers)

# Connect to SQL Database
def connect_to_db():
    # Example for SQLite, change the connection string for other databases
    engine = create_engine('sqlite:///mydatabase.db')
    return engine

# Insert data into SQL
def insert_data_to_sql(df, table_name):
    engine = connect_to_db()
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Main function
def main():
    GOOGLE_SHEET_ID = '1oJ2wAGYLkEd8VeKinrbiAmOwjlZpYqONL09P4LZ01po'
    RANGE_NAME = 'Form Responses 1!A1:L'
    TABLE_NAME = 'responses'
    
    df = read_sheet(GOOGLE_SHEET_ID, RANGE_NAME)
    insert_data_to_sql(df, TABLE_NAME)

if __name__ == '__main__':
    main()
