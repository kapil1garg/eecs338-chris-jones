"""
    This file is used to parse the separated files (generated from clean_data.py) into
    individual fields.

    The `full_text` files have fields found in data/keys.txt
"""
import re
from copy import deepcopy
import json
import os
import elastic
from google_nlp_api import GoogleNlp

PATH_TO_KEYS = 'data/keys.txt'

def get_possible_keys(key_file_path):
    ht = {}
    with open(key_file_path, 'r') as f:
        for k in f.readlines():
            ht[k.rstrip()] = None
    return ht

def parse_document(doc_file_path, allowed_keys):
    # Read in Full Document to be parsed
    with open(doc_file_path, 'r') as f:
        full_doc = f.read()

    # Find locations of matches for all allowed keys
    match_locs = deepcopy(allowed_keys)
    for k in match_locs:
        try:
            match_locs[k] = re.search(k, full_doc).start()
        except AttributeError:
            match_locs[k] = None

    # Get the sorted order of the keys
    matches = {k: v for (k, v) in match_locs.items() if v != None}
    sorted_keys = sorted(matches, key=lambda x: matches[x])

    parsed_data = {}
    for i in range(len(sorted_keys)):
        start_loc = matches[sorted_keys[i]] + len(sorted_keys[i])
        try:
            end_loc = matches[sorted_keys[i + 1]]
        except:
            end_loc = None
        parsed_data[sorted_keys[i]] = full_doc[start_loc:end_loc]
    return parsed_data

def parse_metadata(doc_file_path):
    """
    Parses metadata into dictionary

    inputs:
        doc_file_path (string): full filepath to document

    output:
        (dict): dictionary with parsed metadata
    """
    with open(doc_file_path, 'r') as f:
        meta_data_raw = f.read()

    meta_data_list = [x for x in meta_data_raw.splitlines() if x != '']
    meta_data_dict = {}

    for i in meta_data_list:
        split_string = i.split(':', 1)
        meta_data_dict[split_string[0].strip()] = split_string[1].strip()

    return meta_data_dict

if __name__ == '__main__':
    KEYS = get_possible_keys(PATH_TO_KEYS)
    GOOG = GoogleNlp()
    # print parse_document('data/clean_data/full_text/0114.txt', KEYS)['Full text:']

    ctr = 0
    for f in os.listdir('data/clean_data/full_text')[0:5]:
        if f.endswith('.txt'):
            parsed_document = parse_document('data/clean_data/full_text/' + f, KEYS)
            # google_annotation = GOOG.annotate_text(parsed_document['Full text:'])
            # doc = json.dumps(google_annotation)

            # with open('data/google_results/' + f, 'w') as tmp:
            #     tmp.write(doc)

            # es_url = 'http://search-eecs338-chris-jones-efkwegghpwqww5sfz2225th27y.us-west-2.es.amazonaws.com/'
            # elastic.upload(es_url, 'articles', 'article', str(ctr),
            #                parse_document('data/clean_data/full_text/' + f, KEYS))
            ctr += 1

    for f in os.listdir('data/clean_data/metadata/')[0:5]:
        if f.endswith('.txt'):
            print parse_metadata('data/clean_data/metadata/' + f)

