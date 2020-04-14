'''

updatedata.py -- pulls latest CSVs from ourairports.com

TODO: check if database needs updated via hash

'''
import sys
import os
import wget
import glob

DATA_SOURCE_ROOT = 'https://ourairports.com/data/'

DATA_DIR = "./data/"

DATABASES = [ 'airports.csv',
              'airport-frequencies.csv',
              'runways.csv',
              'navaids.csv',
              'countries.csv',
              'regions.csv']

# Create the data directory if needed
try:
    os.mkdir(DATA_DIR)
except OSError as error:
    for file in glob.glob(DATA_DIR + "*.csv"):
        os.remove(file)

for db in DATABASES:
    wget.download(DATA_SOURCE_ROOT + db, DATA_DIR)

print("\nDatabases updated!")