"""Join csv data to buildings

This script uses the HTTP API, and can process CSV files which identify buildings by id, TOID,
UPRN.

The process:
    - assume first line of the CSV is a header, where column names are either
        - building identifiers - one of:
            - building_id
            - toid
            - uprn
        - building data field names
    - read through lines of CSV:
        - use building id if provided
            - else lookup by toid
            - else lookup by uprn
            - else locate building by representative point
        - update building

TODO extend to allow latitude,longitude or easting,northing columns and lookup by location.

"""
import csv
import json
import os
import sys

import requests


def main(base_url, api_key, source_file):
    """Read from file, update buildings
    """
    with open(source_file, 'r') as source:
        reader = csv.reader(source)
        for line in reader:
            building_id = find_building(line, base_url)

            if building_id is None:
                continue

            update_building(building_id, line, api_key, base_url)


def update_building(building_id, data, api_key, base_url):
    """Save data to a building
    """
    r = requests.post(
        "{}/buildings/{}.json?api_key={}".format(base_url, building_id, api_key),
        json=data
    )


def find_building(data, base_url):
    if 'toid' in data:
        building_id = find_by_reference(base_url, 'toid', data['toid'])
        print("match_by_toid", data['toid'], building_id)
        return building_id

    if 'uprn' in data:
        building_id =  find_by_reference(base_url, 'uprn', data['uprn'])
        print("match_by_uprn", data['uprn'], building_id)
        return building_id

    print("no_match", data)
    return None


def find_by_reference(base_url, ref_key, ref_id):
    """Find building_id by TOID or UPRN
    """
    r = requests.get(base_url + "/buildings/reference", params={
        'key': ref_key,
        'id': ref_id
    })
    buildings = r.json()

    if buildings and len(buildings) == 1:
        building_id = buildings[0]['building_id']
    else:
        building_id = None

    return building_id


if __name__ == '__main__':
    try:
        url, api_key, filename = sys.argv[1], sys.argv[2], sys.argv[3]
    except IndexError:
        print(
            "Usage: {} <URL> <api_key> ./path/to/data.csv".format(
            os.path.basename(__file__)
        ))
        exit()

    main(url, api_key, filename)
