import requests
import json
import elastic
from elastic import ES_URL
from google_nlp_api import GoogleNlp
import re
from QueryAnalyzer import QueryAnalyzer
import random


class ChrisJones:
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        print 'ChrisJones activated'

    def respond(self, query):
        # determine question type
        # then generate appropriate response

        # print query

        annotated_query = self.query_analyzer.get_keywords(query)

        # for now, just return the same stuff all the time
        payload = {"query": {"query_string": {"query": query.encode('utf-8'),
                                          "fields": ["Full text:"]}}}


        r = requests.post(ES_URL + '/flattened-articles/_search', data = json.dumps(payload))
        r = json.loads(r.text)
        r = r['hits']['hits']
        ids = [i['_id'] for i in r]
        print ids


        payload = {
            "_source": ["sentences.content"],
            "query": {
                "bool": {
                    "must": [{
                        "ids": {
                            "values": ids
                        }},
                             {"nested" : {
                                 "path" : "sentences",
                                 "query" : {
                                     "bool": {
                                         "must": [
                                             {"match": {
                                                 "sentences.content": annotated_query['keywords']['NOUN'][0]
                                             }
                                             }
                                         ]
                                     }
                                 },
                                 "inner_hits": {}
                             }}]
                }
            }
           }
        r = requests.post(ES_URL + '/flattened-articles/_search', data = json.dumps(payload))
        r = json.loads(r.text)
        r = [i['inner_hits']['sentences']['hits'] for i in r['hits']['hits']]


        all_sentences = []
        for h in r:
            for i in h['hits']:
                # print i['_source']['content']
                all_sentences.append(i['_source']['content'])
                # print(r)
        return all_sentences[0]


def main():
    query = 'Steppenwolf theatre'
    payload = {"query": {"query_string": {"query": query,
                                          "fields": ["Full text:"]}}}

    r = requests.post('http://search-eecs338-chris-jones-efkwegghpwqww5sfz2225th27y.us-west-2.es.amazonaws.com' + '/flattened-articles/_search', data = json.dumps(payload))
    r = json.loads(r.text)
    r = r['hits']['hits']
    ids = [i['_id'] for i in r]
    print ids


    payload = {
        "_source": ["sentences.content"],
        "query": {
            "bool": {
                "must": [{
                    "ids": {
                        "values": ids
                    }},
                         {"nested" : {
                             "path" : "sentences",
                             "query" : {
                                 "bool": {
                                     "must": [
                                         {"match": {
                                             "sentences.content": "acting"
                                         }
                                         }
                                     ]
                                 }
                             },
                             "inner_hits": {}
                         }}]
            }
        }
    }
    r = requests.post('http://search-eecs338-chris-jones-efkwegghpwqww5sfz2225th27y.us-west-2.es.amazonaws.com' + '/flattened-articles/_search', data = json.dumps(payload))
    r = json.loads(r.text)
    # print(r['hits']['hits'].keys())
    r = [i['inner_hits']['sentences']['hits'] for i in r['hits']['hits']]


    all_sentences = []
    for h in r:
        for i in h['hits']:
            print i['_source']['content']
            # all_sentences.append(i['_source']['content'])
            # print(r)

if __name__ == '__main__':
    main()
