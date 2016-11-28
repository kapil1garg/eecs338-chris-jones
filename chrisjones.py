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
        # Get query annotations
        annotated_query = self.query_analyzer.annotate(query)

        # Route to correct query handler
        if (query == 'how do you like your comedy'):
            return DefaultQuery().generate_response(query, annotated_query)

        elif len(annotated_query.genres) > 0:
            # Genre query handler
            return DefaultQuery().generate_response(query, annotated_query)

        elif any(re.search(i, query) != None for i in ['like', 'dislike', 'love', 'hate']):
            # Sentiment Aggregation query handler
            ess = ElasticSentimentSelection('flattened-articles', 'Full Text:', 'googles', 'documentSentiment')
            best_response = ess.get_best_sentence(query)
            question_type = 'Sentiment Aggregation'
            return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, best_response[0], best_response[1])

        else:
            return DefaultQuery().generate_response(query, annotated_query)


if __name__ == '__main__':
    # Work on query routing now
    cj = ChrisJones()
    query = 'How has the Goodman Theatre changed over time'

    qa = QueryAnalyzer()
    annotated_query = qa.get_keywords(query)
    print cj.route_query(query, annotated_query)

