"""
This module extends the DefaultQuery class to handle sentiment queries
"""
import re
from es_sentiment_selection import ElasticSentimentSelection
from default_query import DefaultQuery

class SentimentQuery(DefaultQuery):
    """
    Handles ES queries related to sentiment
    """

    def __init__(self):
        DefaultQuery.__init__(self)
        self.ess = ElasticSentimentSelection()

    def generate_response(self, query, annotated_query):
        # find what the subject is
        subject = annotated_query.keywords['keywords']['NOUN']
        response = self.ess.get_best_sentence(subject)

        return self.format_response(response)

    def format_response(self, result_tuple):
        article_title = self.clean_article_title(result_tuple[1])

        # Grab sentence from query
        sent = result_tuple[0]

        # Split full text into paragraphs
        article_text = result_tuple[2].splitlines()

        # Find the paragraph with the sentence we want
        response_text = article_text[0] #pick first paragraph as default
        for paragraph in article_text:
            if re.search(sent[:10], paragraph) != None:
                # Add markup formatting
                response_text = paragraph.replace(sent, '*{}*'.format(sent))
                print 'found'
                break
        # Construct and Return response to slackbot
        return '{0}\n_From: {1}_'.format(response_text.encode('utf8'), article_title)
