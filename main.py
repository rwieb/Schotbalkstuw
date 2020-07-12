import csv
import os
from controller.year import *
from controller.database import *

file_import = 'perceel.csv'
file_export = 'export.csv'
sub_regions_dir = 'afstroom_deelgebieden'

constants = {'c': 1075,
             'dividing': 100,
             'save_days_data': True}  # false or true

# remove old database
database_path = 'database.db'
# if os.path.exists(database_path):
#     os.remove(database_path)
# create database class
db = Database(database_path)

#data load
def main():
    all_data = get_data(file_import)
    output = get_sub_regions()
    data_sub_region = output['collection']
    constants['amount_days'] = output['amount_of_days']
    year = Year(constants, db)
    output = year.get_output(all_data, data_sub_region)
    writefile(output, file_export)

#data load
def get_data(file):
    all_data = {}
    with open(file) as f:
        records = csv.DictReader(f, delimiter=';')
        for row in records:
            row = dict(row)
            perceelnr = row['perceelnr']
            if perceelnr != '':
                try:
                    perceelnr = int(perceelnr)
                    all_data[perceelnr] = row
                except ValueError:
                    pass  # it was a string, not an int.
    return all_data

#data load
def get_sub_regions():
    collection = {}
    for filename in os.listdir(sub_regions_dir):
        if filename.endswith(".csv"):
            year = filename.split('_')[0]
            collection[year] = {}
            with open(os.path.join(sub_regions_dir, filename)) as file:
                csv_reader = csv.reader(file, delimiter=';')
                csv_headings = next(csv_reader)
                for region in csv_headings:
                    collection[year][region] = []
                x = 0
                for line in csv_reader:
                    value = 0
                    for region in csv_headings:
                        collection[year][region].append(float(line[value]))
                        value += 1
                    x += 1
                amount_of_days = x
    output = {'collection': collection,
              'amount_of_days': amount_of_days}
    return output


if __name__ == '__main__':
    main()