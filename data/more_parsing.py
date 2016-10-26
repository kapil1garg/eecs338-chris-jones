import re
from copy import deepcopy
import json

"""
    This file is used to parse the separated files (generated from clean_data.py) into
    individual fields.

    The `full_text` files have fields found in data/keys.txt

"""

PATH_TO_KEYS = 'keys.txt'

def getPossibleKeys(keyFilePath):
    ht = {}
    with open(keyFilePath, 'r') as f:
        for k in f.readlines():
            ht[k.rstrip()] = None
    return ht

def parseDocument(docFilePath, allowedKeys):
    # Read in Full Document to be parsed
    with open(docFilePath, 'r') as f:
        full_doc = f.read()

    # Find locations of matches for all allowed keys
    match_locs = deepcopy(allowedKeys)
    for k in match_locs:
        try:
            match_locs[k] = re.search(k, full_doc).start()
        except AttributeError:
            match_locs[k] = None

    # Get the sorted order of the keys
    matches = {k: v for (k, v) in match_locs.items() if v != None}
    sorted_keys = sorted(matches, key = lambda x: matches[x])

    parsed_data = {}
    for i in range(len(sorted_keys)):
        start_loc = matches[sorted_keys[i]]
        try:
            end_loc = matches[sorted_keys[i + 1]]
            print start_loc
            print end_loc
        except:
            end_loc = None
        parsed_data[sorted_keys[i]] = full_doc[start_loc:end_loc]
    return parsed_data









if __name__ == '__main__':
    keez = getPossibleKeys(PATH_TO_KEYS)
    print parseDocument('clean_data/full_text/0114', keez)['Full text:']
