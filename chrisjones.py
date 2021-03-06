"""
This module is the brain of the Chris Jones Bot. It handles queries and constructs responses
"""
import json
import re
import random
import pdb
import requests
from fuzzywuzzy import process

import elastic
from elastic import ES_URL

from google_nlp_api import GoogleNlp
from QueryAnalyzer import QueryAnalyzer
from default_query import DefaultQuery
from default_query import PersonThoughtsQuery
from default_query import LocationQuery
from theater_query import TheaterQuery
from sentiment_query import SentimentQuery
from show_query import ShowQuery


class ChrisJones:
    """
    This is the main class of the Chris Jones Bot
    """
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.sentiment_selector = SentimentQuery()
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
        print annotated_query.get_framework()

        # TODO - change uses of `query` to annotated_query.query to
        # cut back on the number of arguments we have to pass around

        # Route to correct query handler
        if (query == 'how do you like your comedy'):
            print 'comedy query'
            return DefaultQuery().generate_response(query, annotated_query)
        elif (query in ['do you have a favorite actor',
                        'do you have a favorite director',
                        'do you have a favorite actress',
                        'do you have a favorite playwright',
                        'do you have a favorite show',
                        'do you have a favorite theater',
                        'do you have a favorite theatre',
                        'who is your favorite actor',
                        'who is your favorite director',
                        'who is your favorite actress',
                        'who is your favorite playwright',
                        'what is your favorite show',
                        'what is your favorite theater',
                        'what is your favorite theatre']):
            return PersonThoughtsQuery().generate_response_favorite_person(query, annotated_query)

        elif any(re.search(i, query) is not None for i in ['like', 'dislike', 'love', 'hate']):
            # TODO - Determine a more satisfying way to kick off this handler, perhaps it should just be more specific
            # Sentiment Aggregation query handler
            print 'Sentiment Query'
            router = {('do you ' + d + ' ' + t):
                      (lambda x, y: self.sentiment_selector.generate_response(x, y))
                      for t in ['THEATER', 'SHOW', 'GENRE', 'PERSON']
                      for d in ['like', 'dislike', 'hate', 'love']}

            return self.call_handler(router, query, annotated_query)

        elif len(annotated_query.genres) > 0:
            # Genre query handler
            # 'how do you like your GENRE',
            # Write better handler when we get more genre questions
            print 'Genre Query'
            return DefaultQuery().generate_response(query, annotated_query)

        elif len(annotated_query.theaters) > 0:
            # Theater-related questions
            print 'Theater Query'
            router = {
                'what was your favorite show at THEATER': lambda x, y: TheaterQuery().generate_response(x, y),
                'How has THEATER changed over time': lambda x, y: TheaterQuery().generate_response(x, y),
                'I want to go to THEATER. Do you think it is good': lambda x, y: TheaterQuery().generate_response(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        elif len(annotated_query.people) > 0 and len(annotated_query.shows) == 0:
            # People-related questions
            print 'People Query'
            router = {
                'what was PERSON best performance': lambda x, y:
                    PersonThoughtsQuery().generate_response_best_performance(x, y),
                'do you think PERSON is a good NOUN': lambda x, y:
                    PersonThoughtsQuery().generate_response_good_noun(x, y),
                'what do you think of PERSON': lambda x, y: PersonThoughtsQuery().generate_response(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        elif len(annotated_query.shows) > 0:
            # Show related question types
            print 'Show Query'
            router = {
                'what did you think of SHOW': lambda x, y: self.sentiment_selector.generate_response(x, y),
                'what do you think is the best SHOW right now': lambda x, y:
                    ShowQuery().generate_response_best_show(x, y),
                'what do you think of PERSON in SHOW': lambda x, y: ShowQuery().generate_response_person_in_show(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        elif any(re.search(i, query) is not None for i in ['Chicago', 'chicago', 'New York', 'NYC']):
            # Location and/or Chicago-based questions
            print 'Location/Chicago Query'
            router = {
                'what embodies the essence of chicago theater': lambda x, y: LocationQuery().chicago_essence(x, y),
                'how is chicago different from New York?': lambda x, y: LocationQuery().ny_v_chicago(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        else:
            print 'Default Query'
            # What do you think is good NOUN
            return DefaultQuery().generate_response(query, annotated_query)

    def call_handler(self, router, query, annotated_query):
        """
        Helper function to use with query router dictionary switch statements

        args:
            router (dictionary): a dictionary with question frameworks as keys and implementations as values
            query (string): a string with the user's query
            annotated_query (AnnotatedQuery): an AnnotatedQuery corresponding to the user's query
        return:
            response (string): a response string, perhaps with markdown formatting
        """
        question_type = process.extractOne(annotated_query.get_framework(), router.keys())[0]
        return router[question_type](query, annotated_query)


if __name__ == '__main__':
    # Work on query routing now
    cj = ChrisJones()
    query = 'How has the Goodman Theatre changed over time'

    qa = QueryAnalyzer()
    annotated_query = qa.get_keywords(query)
    print cj.route_query(query, annotated_query)
