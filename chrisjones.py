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
from default_query import DefaultQuery


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



    def respond(self, query):
        """
        Main wrapper function for Chris Jones bot. Takes a query and returns a response.
        args:
            query (string): A text query from the user

        return:
            response (string): A string (possibly with markdown formatting)
        """
        annotated_query = self.query_analyzer.annotate(query)
        # question_type = self.route_query(query, annotated_query.keywords)

        # Shoehorning in the Sentiment Queries
        # TODO - Connect with Full Query Router
        # if question_type in [
        #     'do you like NOUN',
        #     'do you hate NOUN',
        #     'do you love NOUN',
        #     'do you dislike NOUN']:
        #     ess = ElasticSentimentSelection('flattened-articles', 'Full Text:', 'googles', 'documentSentiment')
        #     best_response = ess.get_best_sentence(query)
        #     return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, best_response[0], best_response[1])

        # find relevant documents
        # ids = self.get_rel_doc_ids(query)
        return DefaultQuery().generate_response(query, annotated_query)



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



if __name__ == '__main__':
    # Work on query routing now
    cj = ChrisJones()
    query = 'How has the Goodman Theatre changed over time'

    qa = QueryAnalyzer()
    annotated_query = qa.get_keywords(query)
    print cj.route_query(query, annotated_query)

