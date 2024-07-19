'''
Helper class for TransformData class. Downloads images from Googe Drive and inserts to Image table in DB.  

Started: 7/9/2023
Last Updated: 7/9/2024
'''

#####################################################################################################################
## LIBRARIES
#####################################################################################################################

import os
import sqlite3
import requests
import pandas as pd

from PIL import Image
import io

#####################################################################################################################
## Pathing
#####################################################################################################################

# Get the current working directory
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

#####################################################################################################################
## Class
#####################################################################################################################

class ImageWrangler():
    '''
    Takes image download links, downloads images, pass them to images table in DB, and return image_id.
    '''
    def __init__(self, path_to_db):
        self.df = None
        self.path_to_db = path_to_db
        self.connection = None
        self.cur = None
        self.image = None
        self.image_link = None
        self.image_id = None

    def connect(self):
        '''
        Opens connection to DB.
        '''
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(self.path_to_db)
                self.cur = self.connection.cursor()

        except Exception as e:
            print(f"Failed to connected to {self.path_to_db}.", e)


    def close_connection(self):
        '''
        Closes connection to DB.
        '''
        try:
            if self.connection is not None:
                self.connection.close()
                self.connection = None

        except Exception as e:
            print(f"Failed to close connection to {self.path_to_db}.", e)

    def download_image(self):
        '''
        Get image links and download from google drive.
        '''

        try:
            self.connect()

            # Convert Google Drive link to direct download link
            self.image_id = self.image_link.split('=')[1]
            print(f"image_id: {self.image_id}")
            download_url = f"https://drive.google.com/uc?export=download&id={self.image_id}"
            
            # Check if image already exists in db
            existing_image_ids = pd.read_sql(f"SELECT photo_id FROM photos", self.connection)['photo_id'].tolist()
            if self.image_id in existing_image_ids:
                print(f"Image {self.image_id} already exists in table.")
                return None
            
            # Download image data
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                #print("First few bytes of the response content:", response.content[:100])

                # Read the image data into memory
                self.image = response.content
                print(f'Image {self.image_id} downloaded succesfully.')
                
                # Convert the bytes data to an Image object
                #image_data = io.BytesIO(self.image)
                #image = Image.open(image_data)
                # Display the image
                #image.show()

                return True
            else:
                print(f"Failed to download image. HTTP Status Code: {response.status_code}")
                return False
            
        except requests.RequestException as e:
            print(f"Failed to download image. Network error: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
        finally:
            self.close_connection()

    def insert_image(self):
        '''
        Adds image to image table in DB.
        '''
        try:
            self.connect()

            # Insert the image as a BLOB with the unique ID
            self.cur.execute('''
                INSERT INTO photos (photo_id, photo) VALUES (?, ?)
            ''', (self.image_id, self.image))

            # Commit insertion
            self.connection.commit()

            # Get the primary key of the last inserted row
            print(f"Image {self.image_id} inserted successfully.")
            
        except sqlite3.Error as e:
            print(f"An error occured while inserting a image: {e}")
        finally:
            self.close_connection()

    def execute(self, image_link):
        
        # Set attibute values
        self.image_link = image_link

        # Call methods

        if self.download_image():
            self.insert_image()

        # Return image ID
        return self.image_id
        
#####################################################################################################################
## END
#####################################################################################################################
