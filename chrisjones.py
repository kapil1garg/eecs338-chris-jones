"""
This module is the brain of the Chris Jones Bot. It handles queries and constructs responses
"""
import requests
import json
import elastic
from elastic import ES_URL
from google_nlp_api import GoogleNlp
import re
from QueryAnalyzer import QueryAnalyzer
import random
from fuzzywuzzy import process
from es_seniment_selection import ElasticSentimentSelection
import urllib


class ChrisJones:
    """
    This is the main class of the Chris Jones Bot
    """
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.question_types = [
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
            'How has THEATER changed over time',
            'do you like NOUN',
            'do you hate NOUN',
            'do you love NOUN',
            'do you dislike NOUN'
        ]
        print 'ChrisJones activated'

    def get_rel_doc_ids(self, query):
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
        r = requests.post(ES_URL + '/flattened-articles/_search', data = json.dumps(payload))
        r = json.loads(r.text)
        r = r['hits']['hits']
        ids = [i['_id'] for i in r]
        return ids


    def respond(self, query):
        """
        Main wrapper function for Chris Jones bot. Takes a query and returns a response.
        args:
            query (string): A text query from the user

        return:
            response (string): A string (possibly with markdown formatting)
        """
        annotated_query = self.query_analyzer.get_keywords(query)
        question_type = self.route_query(query, annotated_query)

        # Shoehorning in the Sentiment Queries
        # TODO - Connect with Full Query Router
        if question_type in [
            'do you like NOUN',
            'do you hate NOUN',
            'do you love NOUN',
            'do you dislike NOUN']:
            ess = ElasticSentimentSelection('flattened-articles', 'Full Text:', 'googles', 'documentSentiment')
            best_response = ess.get_best_sentence(query)
            return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, best_response[0], best_response[1])

        # find relevant documents
        ids = self.get_rel_doc_ids(query)

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
        # TODO - Replace this with our elastic module, if for no other reason than consistency
        r = requests.post(ES_URL + '/flattened-articles/_search', data = json.dumps(payload))
        r = json.loads(r.text)
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r['hits']['hits']]

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
        return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, response_text,article_title)

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


    def route_query(self, query, keywords):
        """
        Determine the type of question (or the closest) that was asked by the user

        args:
            query (string): the user's text query
            keywords (dictionary): the result of QueryAnalyzer.get_keywords()

        return:
            question_type (string): the type of the question that is closest
        """
        # TODO - Change literally all of this... this is an awful system
        mod_query = self.query_analyzer.get_framework(query, keywords)
        print mod_query
        matches = process.extract(mod_query, self.question_types, limit = 1)
        return matches[0][0]



def main():
    # Work on query routing now
    cj = ChrisJones()
    query = 'How has the Goodman Theatre changed over time'

    qa = QueryAnalyzer()
    annotated_query = qa.get_keywords(query)
    print cj.route_query(query, annotated_query)

if __name__ == '__main__':
    main()
