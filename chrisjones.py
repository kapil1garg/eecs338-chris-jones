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

        # TODO - change uses of `query` to annotated_query.query to cut back on the number of arguments we have to pass around

        # Route to correct query handler
        if (query == 'how do you like your comedy'):
            return DefaultQuery().generate_response(query, annotated_query)

        elif len(annotated_query.genres) > 0:
            # Genre query handler
            ### 'how do you like your GENRE',
            # Write better handler when we get more genre questions
            print 'Genre Query'
            return DefaultQuery().generate_response(query, annotated_query)

        elif len(annotated_query.shows) > 0:
            # Show related question types
            print 'Show Query'
            router = {
                'what did you think of SHOW': lambda x,y: DefaultQuery().generate_response(x, y),
                'what do you think is the best SHOW right now': lambda x,y: DefaultQuery().generate_response(x, y),
                'what do you think of NOUN in SHOW': lambda x,y: DefaultQuery().generate_response(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        elif len(annotated_query.theaters) > 0:
            # Theater-related questions
            print 'Theater Query'
            router = {
            'what was your favorite show at THEATER': lambda x,y: DefaultQuery().generate_response(x, y),
            'How has THEATER changed over time': lambda x,y: DefaultQuery().generate_response(x, y),
            'I want to go to THEATER. Do you think it is good': lambda x,y: DefaultQuery().generate_response(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        elif len(annotated_query.people) > 0:
            # People-related questions
            print 'People Query'
            router = {
            'what was PERSON best performance': lambda x,y: DefaultQuery().generate_response(x, y),
            'do you think PERSON is a good NOUN': lambda x,y: DefaultQuery().generate_response(x, y),
            'what do you think of PERSON': lambda x,y: DefaultQuery().generate_response(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        elif any(re.search(i, query) != None for i in ['like', 'dislike', 'love', 'hate']):
            # TODO - Determine a more satisfying way to kick off this handler, perhaps it should just be more specific
            # Sentiment Aggregation query handler
            print 'Sentiment Query'
            ess = ElasticSentimentSelection('flattened-articles', 'Full Text:', 'googles', 'documentSentiment')
            best_response = ess.get_best_sentence(query)
            question_type = 'Sentiment Aggregation'
            return '*Q:* {0}\n*A:* {1}\n*From*: {2}'.format(question_type, best_response[0], best_response[1])

        elif any(re.search(i, query) != None for i in ['Chicago', 'chicago', 'New York', 'NYC']):
            # Location and/or Chicago-based questions
            print 'Location/Chicago Query'
            router = {
                'what embodies the essence of chicago theater': lambda x,y: DefaultQuery().generate_response(x, y),
                'how is chicago different from New York?': lambda x,y: DefaultQuery().generate_response(x, y)
            }
            # Find the closest question type and use it to access handler
            return self.call_handler(router, query, annotated_query)

        else:
            print 'Default Query'
            ### What do you think is good NOUN
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

