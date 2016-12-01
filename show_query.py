import json
import re
import elastic
import numpy
from operator import itemgetter
from default_query import DefaultQuery

class ShowQuery(DefaultQuery):
    """
    Handles ES queries related to shows
    """
    def __init__(self):
        DefaultQuery.__init__(self)

    def generate_response_best_show(self, query, annotated_query):
        # find document id with max polarity
        payload = {
            '_source': ['documentSentiment.polarity'],
            'query': {
                'bool': {
                    'must': [{
                        'match': {
                            'Full text:': p
                        }}
                             for p in annotated_query.shows]
                }
            }
        }

        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        polarities = [(i['_id'], i['_source']['documentSentiment']['polarity']) for i in r]
        id_max_polarity = max(polarities, key=itemgetter(1))[0]

        # return sentence from document id that contains show in a sentence
        payload = {
            '_source': ['sentences.content', 'Full text:', 'ProQ:'],
            'query': {
                'bool': {
                    'must': [{
                        'ids': {
                            'values': [id_max_polarity]
                        }},
                             {'nested' : {
                                 'path' : 'sentences',
                                 'query' : {
                                     'bool': {
                                         'must': [{'match': {'sentences.content': p}} for p in annotated_query.shows]
                                     }
                                 },
                                 'inner_hits': {}
                             }}]
                }
            }
        }
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        return self.format_response(r[0])

    def generate_response_person_in_show(self, query, annotated_query):
        match_queries = [{
                'match': {
                    'Full text:': show
                }
            }
            for show in annotated_query.shows
        ]
        match_queries.append({
            'nested': {
                'path': 'sentences',
                'query': {
                    'bool': {
                        'must': [{
                                'match': {
                                    'sentences.content': p
                                }
                            }
                            for p in annotated_query.people
                        ]
                    }
                },
                'inner_hits': {}
            }
        })
        payload = {
            '_source': ['sentences.content', 'Full text:', 'ProQ:'],
            'query': {
                'bool': {
                    'must': match_queries
                }
            }
        }

        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        return self.format_response(r[0])
