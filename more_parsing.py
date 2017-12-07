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

from multiprocessing import Pool
from google_nlp_api import GoogleNlp
from tqdm import tqdm

PATH_TO_KEYS = 'data/keys.txt'


def get_possible_keys(key_file_path):
    """
    Retrieves pre-made list of keys to use for parsing

    inputs:
        key_file_path (string): file path

    outputs:
        (list): list of keys for parsing
    """
    key_dict = {}
    with open(key_file_path, 'r') as file_name:
        for k in file_name.readlines():
            key_dict[k.rstrip()] = None
    return key_dict


def parse_document(doc_file_path, allowed_keys):
    """
    Parses cleaned text into dictionary

    inputs:
        doc_file_path (string): file path to string
        allowed_keys (list): list of valid keys

    outputs:
        (dict): file parsed into dictionary
    """
    # read in Full Document to be parsed
    with open(doc_file_path, 'r') as file_name:
        full_doc = file_name.read()

    # find locations of matches for all allowed keys
    match_locs = deepcopy(allowed_keys)
    for k in match_locs:
        try:
            match_locs[k] = re.search(k, full_doc).start()
        except AttributeError:
            match_locs[k] = None

    # get the sorted order of the keys
    matches = {k: v for (k, v) in match_locs.items() if v is not None}
    sorted_keys = sorted(matches, key=lambda x: matches[x])

    # parse file
    parsed_data = {}
    for i in range(len(sorted_keys)):
        start_loc = matches[sorted_keys[i]] + len(sorted_keys[i])
        try:
            end_loc = matches[sorted_keys[i + 1]]
        except Exception:
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
    with open(doc_file_path, 'r') as file_name:
        meta_data_raw = file_name.read()

    meta_data_list = [x for x in meta_data_raw.splitlines() if x != '']
    meta_data_dict = {}

    for i in meta_data_list:
        split_string = i.split(':', 1)
        meta_data_dict[split_string[0].strip()] = split_string[1].strip()

    return meta_data_dict


def get_annotation_for_file(file_name):
    """
    Gets annotations from google's NLP API in parallel

    inputs:
        filenames (list of strings): list of files to annotate
    """
    keys = get_possible_keys(PATH_TO_KEYS)
    google = GoogleNlp()

    parsed_document = parse_document('data/clean_data/full_text/' + file_name, keys)
    google_annotation = google.annotate_text(parsed_document['Full text:'])
    doc = json.dumps(google_annotation)

    # write annotations to disk
    with open('data/google_results/' + file_name, 'w') as tmp:
        tmp.write(doc)


def main():
    """
    Function called when module called from command line
    """

    # only upload files that don't have annotations yet
    parsed_google_files = set(os.listdir('data/google_results'))
    files_to_upload = [file for file in os.listdir('data/clean_data/full_text')
                       if file.endswith('.txt') and file not in parsed_google_files]

    # start multithreading pool
    processors = 4
    pool = Pool(processors)
    r = list(tqdm(pool.imap(get_annotation_for_file, files_to_upload), total=len(files_to_upload)))

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
