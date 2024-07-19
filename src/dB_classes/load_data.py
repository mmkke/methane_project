'''
Class for loading transformed data in into DB.

Started: 6/15/2023
Last Updated: 7/6/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################

import sqlite3
import pandas as pd

#####################################################################################################################
## CLASS
#####################################################################################################################

class LoadData():
    def __init__(self, path_to_db):
        self.path_to_db = path_to_db
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.path_to_db)

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def insert_data_to_sql(self, df, table_name):
        '''
        Adds df_formated to sql.
        '''
        try:
            self.connect()
            print(df)

            # CHeck existing records
            existing_timestamps = pd.read_sql(f"SELECT timestamp FROM {table_name}", self.connection)['timestamp'].tolist()
            new_data = df[~df['timestamp'].isin(existing_timestamps)]

            # Insert new data
            if not new_data.empty:
                new_data.to_sql(table_name, self.connection, if_exists='append', index=False)
                print(f"Inserted {len(new_data)} new records into the database.")
            else:
                print("No new records to insert.")

        except Exception as e:
            print(f"Failed to insert data into the SQL table: {e}")
            raise
        finally:
            self.close_connection()

    def check_table(self, table_name):
        try:
            self.connect()

            # Read the table into a pandas DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connection)

            # Display the DataFrame
            print(df.columns)
            print(df)

        except Exception as e:
            print(f"Failed to query SQL table: {e}")
            raise
        finally:
            self.close_connection()
    

#####################################################################################################################
## END
#####################################################################################################################