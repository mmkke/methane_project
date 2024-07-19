'''
Driver for running ETL pipeline. 

Started: 7/6/2023
Last Updated: 7/19/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################

import os
from pathlib import Path

#####################################################################################################################
## Pathing
#####################################################################################################################

# Get the current working directory
current_dir = Path.cwd()
print(f"Current working directory: {current_dir}")

#####################################################################################################################
## Modules
#####################################################################################################################

from manage_methane_db import MethaneDB
from fetch_data_from_api import FetchData
from transform_data import TransformData
from load_data import LoadData
from etl_pipeline import ETLPipeline

#####################################################################################################################
## Parameters
#####################################################################################################################

DATABASE = "methane_project_DB"
DB_FOLDER_PATH = current_dir / "data"
CREDENTIALS_PATH = 'credentials.json'
GOOGLE_SHEET_ID = '1oJ2wAGYLkEd8VeKinrbiAmOwjlZpYqONL09P4LZ01po'
RANGE_NAME = 'Form Responses 1!A1:G'
TABLE_NAME = "measurements"

#####################################################################################################################
## Main
#####################################################################################################################

def main():

    # Check if the folder exists, if not create it
    if not DB_FOLDER_PATH.exists():
        DB_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
    print(f"Directory {DB_FOLDER_PATH} exists: {DB_FOLDER_PATH.exists()}")

    # set path to db file
    PATH_TO_DB = DB_FOLDER_PATH / DATABASE
    
    database = MethaneDB(PATH_TO_DB)
    fetcher = FetchData(CREDENTIALS_PATH, GOOGLE_SHEET_ID, RANGE_NAME)
    transformer = TransformData(PATH_TO_DB)
    loader = LoadData(PATH_TO_DB)

    pipe = ETLPipeline(database,
                       fetcher,
                       transformer,
                       loader)
    
    pipe.pipe_data_to(TABLE_NAME)
    
    # Check db contents
    #database.print_all_tables_and_values()
    query='''SELECT * FROM photos'''
    df = database.query_db(query)

#####################################################################################################################
## END
#####################################################################################################################
if __name__ == '__main__':
    main()

#####################################################################################################################
## END
#####################################################################################################################