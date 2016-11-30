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
    print r
    print "\n\n\n"
    r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]
    print r

    # TODO - This is hella sloppy, replace all this with something robust and coherent

    article_title = self.clean_article_title(r[0][1])

    # Grab sentence from query
    sent = r[0][0]['hits'][0]['_source']['content']
    # Split full text into paragraphs
    article_text = r[0][2].splitlines()
    # Find the paragraph with the sentence we want
    response_text = article_text[0] #pick first paragraph as default
    for p in article_text:
        if re.search(sent[:10], p) != None:
            # Add markup formatting
            response_text = p.replace(sent, '*{}*'.format(sent))
            print 'found'
            break
    # Construct and Return response to slackbot
    question_type = 'Theater'
    return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, response_text.encode('utf8'), article_title)

