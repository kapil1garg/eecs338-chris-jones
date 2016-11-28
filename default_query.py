"""
This module is used to handle default queries
"""
import json
import re
import elastic
import urllib

class DefaultQuery(object):
    """
    Implements the default query-handling logic
    """
    def __init__(self):
        self.dummy = 0

    def get_relevant_document_ids(self, query):
        """
        Get the relevant document ids from Elastic Search for a full text query

        args:
            query (string): A text string to be used on a full-text query

        return:
            ids (list): A list of document IDs
        """
        payload = {
            "query": {
                "query_string": {
                    "query": query.encode('utf-8'),
                    "fields": ["Full text:"]
                }
            }
        }

        # TODO - Replace this with our elastic module, if for no other reason than consistency
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        ids = [i['_id'] for i in r]
        return ids

    def clean_article_title(self, title):
        """
        Take an article-source URL and return a cleanly formatted title

        args:
            title (string): a source URL

        return:
            article_title (string): A cleanly formatted title to include in response
        """
        article_title = urllib.unquote(title)
        article_title = re.split('title=', article_title)[1].replace('+', ' ').decode('utf8')
        title_len = len(article_title)
        if (article_title[title_len - 5:] in ['&amp', '&amp;']):
            article_title = article_title[:title_len - 5]
        return article_title

    def generate_response(self, query, annotated_query):
        ids = self.get_relevant_document_ids(query)

        # Make Fall-back ES Query
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
                                             {"match": {
                                                 "sentences.content": annotated_query.keywords['keywords']['NOUN'][0]
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
        # TODO - Replace this with our elastic module, if for no other reason than consistency
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        # TODO - This is hella sloppy, replace all this with something robust and coherent

        article_title = self.clean_article_title(r[0][1])

        # Grab sentence from query
        sent = r[0][0]['hits'][0]['_source']['content']
        # Split full text into paragraphs
        article_text = r[0][2].splitlines()
        # Find the paragraph with the sentence we want
        for p in article_text:
            if re.search(sent, p) != None:
                # Add markup formatting
                response_text = p.replace(sent, '*{}*'.format(sent))
                break
        # Construct and Return response to slackbot
        question_type = 'asdf'
        return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, response_text,article_title)







