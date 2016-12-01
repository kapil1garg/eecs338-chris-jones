from default_query import DefaultQuery
import json
import re
import elastic
import urllib

class TheaterQuery(DefaultQuery):
  """
  Handles ES queries related to theaters
  """

  def __init__(self):
    DefaultQuery.__init__(self)

  def generate_response(self, query, annotated_query):
    theater = annotated_query.theaters[0]
    ids = self.get_relevant_document_ids(theater)
    at_theater = "at "+theater
    payload = {
        "_source": ["sentences.content", "Full text:", "ProQ:"],
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
                                         {"match" : {"sentences.content":theater}},
                                         {"match" : {"sentences.content":at_theater}}
                                     ]
                                 }
                             },
                             "inner_hits": {}
                         }}]
            }
        }
    }
    r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
    r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]


    return self.format_response(r[0], question_type = 'Theater')
