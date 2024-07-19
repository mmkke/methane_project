'''
Class for creating and managing methane database.

Started: 6/15/2023
Last Updated: 7/19/2024
'''
#####################################################################################################################
## Libraries
#####################################################################################################################

import os
from pathlib import Path
import sqlite3
import pandas as pd

#####################################################################################################################
## Class
#####################################################################################################################

class MethaneDB:
    '''
    Creates and manages sql database for Sierra Club Methane Project
    '''

    def __init__(self, path_to_db) -> None:
        self.path_to_db = path_to_db
        self.connection = None
        self.cur = None

    def connect(self):
        '''
        Connects to DB.
        '''
        if self.connection is None:
            self.connection = sqlite3.connect(self.path_to_db)
            self.cur = self.connection.cursor()

    def close_connection(self):
        '''
        Closes connection to DB.
        '''
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def create(self):
        """
        Sets up DB tables if they do not already exist.
        """
        # connect to db
        self.connect()

        ## define tables

        # cities
        create_table_cities =                   '''
                                                CREATE TABLE IF NOT EXISTS cities(
                                                    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    city VARCHAR UNIQUE,
                                                    county VARCHAR,
                                                    state VARCHAR DEFAULT "MAINE",
                                                    utility_provider VARCHAR,
                                                    FOREIGN KEY (utility_provider) REFERENCES utility_providers(company_name)
                                                    )
                                                '''
        # utility provider
        create_table_utility_providers =       '''
                                                CREATE TABLE IF NOT EXISTS utility_providers(
                                                    provider_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    company_name VARCHAR UNIQUE,
                                                    mailing_address TEXT,
                                                    phone_number VARCHAR,
                                                    region VARCHAR
                                                    )
                                                '''
        
        # measurements
        create_table_measurements =             '''
                                                CREATE TABLE IF NOT EXISTS measurements(
                                                    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    city VARCHAR,
                                                    methane_level FLOAT,
                                                    leak BOOL,
                                                    type_of_infrastructure TEXT,
                                                    photo_id VARCHAR,
                                                    latitude FLOAT,
                                                    longitude FLOAT,
                                                    volunteer VARCHAR,
                                                    timestamp TIMESTAMP UNIQUE,
                                                    FOREIGN KEY (city) REFERENCES cities(city),
                                                    FOREIGN KEY (photo_id) REFERENCES photos(photo_id)
                                                    )
                                                '''
        # photos
        create_table_photos =                   '''
                                                CREATE TABLE IF NOT EXISTS photos(
                                                    photo_id VARCHAR PRIMARY KEY,
                                                    photo BLOB                                                    
                                                    )
                                                '''
        # volunteers
        create_table_volunteers =       '''
                                                CREATE TABLE IF NOT EXISTS volunteers(
                                                    volunteer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    first_name VARCHAR,
                                                    last_name VARCHAR,
                                                    city VARCHAR,
                                                    initials VARCHAR,
                                                    FOREIGN KEY (city) REFERENCES cities(city)
                                                    )
                                                '''
        # execute sql commands
        self.cur.execute(create_table_cities)
        self.cur.execute(create_table_utility_providers)
        self.cur.execute(create_table_measurements)
        self.cur.execute(create_table_photos)
        self.cur.execute(create_table_volunteers)

        #print tables
        self.print_all_tables()

        # close connection
        self.close_connection()
    

    def add_volunteer(self, first_name, last_name, initials, city):
        """
        Adds volunteer record to volunteer table.
        """
        try:
            self.connect()
            insert_query =  """
                            INSERT INTO volunteers (first_name, last_name, initials, city)
                            VALUES (?, ?, ?, ?);
                            """
            self.cur.execute(insert_query, (first_name, last_name, initials, city))
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"An error occurred while adding a volunteer: {e}")
        finally:
            if self.connection:
                self.connection.close()   

    def add_utility_provider(self, company_name, mailing_address, phone_number, region):
        """
        Adds utility provider record to utility_providers table.
        """
        try:
            self.connect()
            insert_query =  """
                            INSERT INTO utility_providers (company_name, mailing_address, phone_number, region)
                            VALUES (?, ?, ?, ?);
                            """
            self.cur.execute(insert_query, (company_name, mailing_address, phone_number, region))
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"An error occured while adding a utility_provider: {e}")
        finally:
            self.close_connection()
        

    def add_city(self, city_name, city_county, city_state, city_utility_provider):
        """
        Adds volunteer record to volunteer table.
        """
        try:
            self.connect()
            insert_query =  """
                            INSERT INTO cities (city_name, city_county, city_state, city_utility_provider)
                            VALUES (?, ?, ?, ?);
                            """
            self.cur.execute(insert_query, (city_name, city_county, city_state, city_utility_provider))
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"An error occured whil adding a city: {e}")
        finally:
            self.close_connection()

    def add_image(self, idx, image_data):
        '''
        Adds image to photo table and returns photo_id value.
        '''
        try:
            self.connect()

            # Create table if it doesn't exist
            self.cur.execute('''
                        CREATE TABLE IF NOT EXISTS photos(
                            photo_id INTEGER PRIMARY KEY,
                            photo BLOB
                            )
                        ''')
            
            # Insert the image as a BLOB with the unique ID
            self.cur.execute('''
                INSERT INTO photos (photo_id, photo) VALUES (?, ?)
            ''', (idx, image_data))

            # Get the primary key of the last inserted row
            photo_id = self.cur.lastrowid
            print(f"Image inserted into the database with photo_id: {photo_id}")
            return photo_id 
        
        except sqlite3.Error as e:
            print(f"An error occured whil adding a city: {e}")
        finally:
            self.close_connection()


    def insert_data_to_sql(self, df, table_name):
        '''
        Adds df_formated to sql.
        '''
        try:
            # open db connection
            self.connect()

            # insert data
            df.to_sql(table_name, con=self.connection, if_exists='append', index=False)
            print("Data inserted successfully")

        except Exception as e:
            print(f"Failed to insert data into the SQL table: {e}")
            raise
        finally:
            self.close_connection()


    def print_all_tables(self):
        """ 
        Prints all tables and their attributes
        """
        try:
            # Connect to the SQLite database
            self.connect()
        
            # Query to get the names of all tables
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cur.fetchall()
            
            if tables:
                print("Tables and their columns:")
                for table in tables:
                    table_name = table[0]
                    print(f"\nTable: {table_name}")
                    
                    # Query to get columns for each table
                    self.cur.execute(f"PRAGMA table_info({table_name});")
                    columns = self.cur.fetchall()
                    
                    for column in columns:
                        column_id, column_name, column_type, not_null, default_value, is_pk = column
                        print(f"  Column: {column_name}, Type: {column_type}, Not Null: {not_null}, Default: {default_value}, Primary Key: {is_pk}")
                    
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the connection
            self.close_connection()


    def print_all_tables_and_values(self):
        # Connect to the SQLite database
        self.connect()

        # Fetch all table names
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cur.fetchall()

        # Iterate over each table and fetch its values
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            
            # Fetch all data from the table
            self.cur.execute(f"SELECT * FROM {table_name};")
            rows = self.cur.fetchall()

            # Fetch column names
            self.cur.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in self.cur.fetchall()]
            print("Columns:", columns)

            # Print each row
            for row in rows:
                print(row)
            
            print("\n")

        # Close the connection
        self.close_connection()

    def query_db(self, query):
        '''Executes a generic query.'''
        try:
            # Connect to the SQLite database
            self.connect()
            
             # Execute the provided query and return the result as a DataFrame
            results_df = pd.read_sql_query(query, self.connection)
            return results_df
             
        except Exception as e:
            print(f"An error occurred while executing the query: {str(e)}")
        finally:
            # Close the connection
            self.close_connection()
#####################################################################################################################
## END
#####################################################################################################################
