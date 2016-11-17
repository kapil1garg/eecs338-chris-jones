import requests
import json
import elastic
from elastic import ES_URL
from google_nlp_api import GoogleNlp
import re
from QueryAnalyzer import QueryAnalyzer
import random
from fuzzywuzzy import process


class ChrisJones:
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        print 'ChrisJones activated'

    def get_rel_doc_ids(self, query):
        payload = {
            "query": {
                "query_string": {
                    "query": query.encode('utf-8'),
                    "fields": ["Full text:"]
                }
            }
        }

        r = requests.post(ES_URL + '/flattened-articles/_search', data = json.dumps(payload))
        r = json.loads(r.text)
        r = r['hits']['hits']
        ids = [i['_id'] for i in r]
        return ids


    def respond(self, query):
        # determine question type
        # then generate appropriate response

        annotated_query = self.query_analyzer.get_keywords(query)

        # find relevant documents
        ids = self.get_rel_doc_ids(query)

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
    # Work on query routing now
    question_types = [
        'what do you think is good NOUN',
        'I want to got to THEATER. Do you think it is good',
        'what did you think of SHOW',
        'what do you think of NOUN in SHOW',
        'what do you think of ACTOR',
        'do you think ACTOR is a good NOUN',
        'what is the best performance right now',
        'what was your favorite show at THEATER',
        'what was ACTOR best performance',
        'how do you like your GENRE',
        'what embodies the essence of chicago theater',
        'how is chicago different from New York?',
        'How has THEATER changed over time'
    ]

    query = 'How has the Goodman changed over time'

    qa = QueryAnalyzer()
    annotated_query = qa.get_keywords(query)
    mod_query = qa.get_framework(query, annotated_query)

    print mod_query

    matches = process.extract(mod_query, question_types, limit = 1)
    print matches

if __name__ == '__main__':
    main()
