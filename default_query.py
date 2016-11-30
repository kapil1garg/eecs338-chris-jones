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
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        return self.format_response(r[0])

    def format_response(self, result_tuple, question_type = 'Default'):

        article_title = self.clean_article_title(result_tuple[1])

        # Grab sentence from query
        sent = result_tuple[0]['hits'][0]['_source']['content']
        # Split full text into paragraphs
        article_text = result_tuple[2].splitlines()
        # Find the paragraph with the sentence we want
        response_text = article_text[0] #pick first paragraph as default
        for p in article_text:
            if re.search(sent[:10], p) != None:
                # Add markup formatting
                response_text = p.replace(sent, '*{}*'.format(sent))
                print 'found'
                break
        # Construct and Return response to slackbot
        return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, response_text.encode('utf8'), article_title)



class PersonThoughtsQuery(DefaultQuery):


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
                                         "should":


                                         [ {"match": {"sentences.content": i}} for i in ['strong', 'dynamic', 'elegant', 'up-and-coming', 'powerful', 'good', 'bad', 'excellent', 'flat', 'disappointing', 'shocking', 'emerging', 'growing', 'riveting', 'depressing', 'awful', 'focused', 'intelligent', 'smart', 'subtle', 'outstanding', 'accomplished', 'terrific', 'great', 'love', 'hate', 'like']],
                                         "must": {"match": {"sentences.content": annotated_query.people[0]}}

                                     }
                                 },
                                 "inner_hits": {}
                             }}]
                }
            }
        }
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        return self.format_response(r[0], question_type = 'What do you think of PERSON')





    def generate_response_best_performance(self, query, annotated_query):
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
                                         "should":


                                         [ {"match": {"sentences.content": i}} for i in ['strong', 'dynamic', 'elegant', 'powerful', 'good', 'excellent', 'shocking', 'emerging', 'riveting', 'focused', 'intelligent', 'smart', 'subtle', 'outstanding', 'accomplished', 'terrific', 'great', 'love', 'performance', 'favorite', 'best', 'portral', 'cast']],
                                         "must": {"match": {"sentences.content": annotated_query.people[0]}}

                                     }
                                 },
                                 "inner_hits": {}
                             }}]
                }
            }
        }
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        return self.format_response(r[0], question_type = 'What was PERSON best performance')
