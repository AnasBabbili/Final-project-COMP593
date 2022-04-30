""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation
"""
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
from os import path
import requests
import shutil
import sqlite3
import datetime
import os.path
import os
import ctypes
import hashlib

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = download_apod_image(apod_info_dict)
    image_msg = image_url
    image_url_encoded = hashlib.sha256(image_url.encode())
    image_sha256 = str(image_url_encoded.digest())
    image_size = len(image_path)
    image_path = get_image_path(image_url, image_dir_path)

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    desktop_background = os.path.join(image_url)
    set_desktop_background_image(desktop_background)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    url = image_url

    image_path = dir_path

    full_path = os.path.join(image_path)
    print("Image full path is", full_path)

    return image_path

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    NASA_Api = 'https://api.nasa.gov/planetary/apod?api_key='
    my_api_key = 'Zlpff777pdr4i11KDS3DP5tWpcnicT9DqTifgKY7'
    print('Getting APOD information...', end='')

    parameters = (NASA_Api + my_api_key + "&date" + date)

    response = requests.get(parameters)

    if response.status_code == 200:
        print('success')

        APOD_info = response.json()

        APOD_dict = dict(APOD_info)

        return APOD_dict

    else:
        print('Failed. Response code:', response.status_code)
        return

def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """    
    print('The URL of the APOD image is', image_url)
    print('The full path of the APOD image is', image_path)
    print('The size of the APOD image is', image_size)
    print('The hash value of the APOD image is', image_sha256)


def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    print('Downloading APOD image...', end='')
    APOD_image_url = image_url['url']

    APOD_image_info = requests.get(APOD_image_url)

    if APOD_image_info.status_code == 200:
        print('success')
        return APOD_image_url
    else:
        print('Failed to download APOD image. Response code:', APOD_image_url.status_code)

def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    print('Saving image file...', end='')
    url = image_msg

    response = requests.get(url).content

    if response.status_code == 200:
        print('success')
    else:
        print('Failed to save image file. Response code:', response.status_code)
    
    with open('APOD_image.jpg', 'wb') as handler:
        handler.write(response)

def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """
    image_path = db_path

    db_path = sqlite3.connect(image_path)

    cursor = db_path.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS 'APOD Images'
            (image_path text,
            image_url text,
            image_size integer,
            image_sha256 text)
            """
            ) 

    db_path.commit()

    db_path.close()

    return 

def add_image_to_db(db_path, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    cxn = sqlite3.connect(db_path)

    cursor = cxn.cursor()

    cursor.execute("""INSERT INTO 'APOD Images'
        (image_path,
        image_url,
        image_size,
        image_sha256)
        VALUES (?, ?, ?, ?)""",
        (db_path, image_path, image_size, image_sha256))

    cxn.commit()

    cxn.close()

    return

def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
    cxn = sqlite3.connect(db_path)

    cursor = cxn.cursor()

    cursor.execute("SELECT 'image_sha256' FROM 'APOD images'")

    hash_of_images = cursor.fetchall()

    cxn.close()

    if image_sha256 in hash_of_images:
        return True
    else:
        return False

def set_desktop_background_image(image_path):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path , 0)
    print('Desktop wallpaper has been changed.')
    return

main()