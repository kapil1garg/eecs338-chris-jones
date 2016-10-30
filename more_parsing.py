import re
from copy import deepcopy
import json
import os
import elastic
from google_nlp_api import GoogleNlp

"""
    This file is used to parse the separated files (generated from clean_data.py) into
    individual fields.

    The `full_text` files have fields found in data/keys.txt

"""

PATH_TO_KEYS = 'data/keys.txt'

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
        start_loc = matches[sorted_keys[i]] + len(sorted_keys[i])
        try:
            end_loc = matches[sorted_keys[i + 1]]
        except:
            end_loc = None
        parsed_data[sorted_keys[i]] = full_doc[start_loc:end_loc]
    return parsed_data









if __name__ == '__main__':
    keez = getPossibleKeys(PATH_TO_KEYS)
    goog = GoogleNlp()
    # print parseDocument('data/clean_data/full_text/0114.txt', keez)['Full text:']
    ctr = 0
    for f in os.listdir('data/clean_data/full_text'):
        if f.endswith('.txt'):
            doc = json.dumps(goog.annotate_text(parseDocument('data/clean_data/full_text/' + f, keez)['Full text:']))
            with open('data/google_results/' + f, 'w') as tmp:
                tmp.write(doc)
            # elastic.upload('http://search-eecs338-chris-jones-efkwegghpwqww5sfz2225th27y.us-west-2.es.amazonaws.com/', 'articles', 'article', str(ctr), parseDocument('data/clean_data/full_text/' + f, keez))
            ctr = ctr + 1
