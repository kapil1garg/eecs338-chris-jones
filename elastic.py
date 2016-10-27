import requests
import json

ES_URL = "http://search-eecs338-chris-jones-efkwegghpwqww5sfz2225th27y.us-west-2.es.amazonaws.com/"


def upload(url, index, doc_type, idx, data):
    requests.post(url + '/' + index + '/' + doc_type + '/' + idx, json.dumps(data))

def search(url, index, data):
    r = requets.post(url + '/' + index, data = json.dumps(data))
    return r.text
