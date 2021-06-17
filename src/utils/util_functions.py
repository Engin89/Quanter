import pandas as pd
from datetime import datetime
import os
import sys
import fileinput
import yaml

sys.path.append('../data')


def get_keys():
    with open('../data/params.yml') as f:
        parsed_yaml_file = yaml.load(f, Loader=yaml.FullLoader)
        api_url = 'https://www.alphavantage.co/query'
        return parsed_yaml_file.get('ALPHAVANTAGE_API_KEY'), api_url


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


def openloghistory():
    loghistory = os.path.join('../data', 'loghistory.txt')
    with open(loghistory, 'r') as f:
        for line in f:
            if '*' in line:
                start, end = int(line.split(' ')[0]), int(line.split(' ')[1])
    return start, end


def replaceloghistory(start, end):
    file = os.path.join('../data', 'loghistory.txt')
    dt = str(datetime.today().strftime("%y-%m-%d %H:%M:%S"))
    searchExp = f'{start} {end} *\n'
    replaceExp = f'{start} {end} * Y {dt}\n'
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)
