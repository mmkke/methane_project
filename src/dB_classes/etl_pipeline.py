'''
Class for running ETL pipeline. 

Started: 7/6/2023
Last Updated: 7/6/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################

#####################################################################################################################
## CLASS
#####################################################################################################################

class ETLPipeline():
    def __init__(self, database, fetcher, transformer, loader):
        self.db = database
        self.fetcher = fetcher
        self.transformer = transformer
        self.loader = loader

    def pipe_data_to(self, table_name):

        # Set up database
        self.db.create()

        # Fetch data from the Google Sheet's API
        raw_data = self.fetcher.execute()

        # Tranform Data
        transformed_data = self.transformer.execute(raw_data)

        # Load Data
        self.loader.insert_data_to_sql(transformed_data, table_name)

        # Show Data
        self.loader.check_table(table_name)


#####################################################################################################################
## END
#####################################################################################################################