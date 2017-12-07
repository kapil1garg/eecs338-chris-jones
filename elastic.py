"""
This module is used to query elastic search
"""
import json
import requests

ES_URL = "https://search-chris-jones-demo-tvyrpelzvfovopq4dss46qojdq.us-west-2.es.amazonaws.com"


def upload(url, index, doc_type, idx, data):
    """
    Uploads new data to elastic search

    inputs:
        url (string): elastic search URL
        index (string): index to upload to
        doc_type (string): document type to upload to index
        idx (int): id number
        data (dict): dictionary of data to upload
    """
    requests.post(url + '/' + index + '/' + doc_type + '/' + idx, json.dumps(data))


def search(url, index, data):
    """
    Searches ES

    inputs:
        url (string): elastic search URL
        index (string): index to search
        data (dict): dictionary representing query payload

    output:
        (string): response from ES
    """
    es_request = requests.post(url + '/' + index, data=json.dumps(data))
    return es_request.text
