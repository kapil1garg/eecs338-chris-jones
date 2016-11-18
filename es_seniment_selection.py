"""
This module is used to find key words and phrases in the articles index and map the
text to sentiment values in the googles index
"""
import json
import numpy as np
import elastic
import re

class ElasticSentimentSelection(object):
    """
    Conducts a search on an index and then finds a matching document
    in another index where sentiment is kept by id match
    """
    def __init__(self, search_index, text_search_field, sentiment_index, sentiment_field):
        self.search_index = search_index
        self.text_search_field = text_search_field
        self.sentiment_index = sentiment_index
        self.sentiment_field = sentiment_field
        self.curr_relevant_documents = {}

    def get_sentiment_for_phrase(self, search_phrase):
        """
        Computes average sentiment from all relevant documents returned from search.

        inputs:
            search_phrase (string): string to search for in ES

        output:
            (float): average polarity from all related documents
        """
        # get relevant documents
        relevant_documents = self.get_relevant_documents(search_phrase)
        self.curr_relevant_documents = relevant_documents

        # return average polarity for phrase
        average_polarity = 0
        for i in relevant_documents['hits']['hits']:
            average_polarity += float(i['_source']['documentSentiment']['polarity'])

        return average_polarity / (len(relevant_documents.keys()) + 0.0000001)

    def get_best_sentence(self, search_phrase):
        # get sentiment for phrase
        average_sentiment = self.get_sentiment_for_phrase(search_phrase)

        # get relevant documents
        relevant_documents = self.get_relevant_documents(search_phrase)['hits']['hits']

        # find closest document
        closest_doc = self.get_closest_document(average_sentiment)

        # find sentence with most i's
        top_sentence = self.sentence_most_i(closest_doc)

        return top_sentence

    def get_closest_document(self, sentiment):
        closest = {}
        closest_value = 10000000

        for i in self.curr_relevant_documents['hits']['hits']:
            current_diff = abs(i['_source']['documentSentiment']['polarity'])

            if current_diff < closest_value:
                closest = i
                closest_value = current_diff

        return closest

    def sentence_most_i(self, closest_doc):
        top_text = ''
        top_text_i = 0

        for i in closest_doc['_source']['sentences']:
            curr_i = len(re.findall('I', i['content']))
            if curr_i > top_text_i:
                top_text = i['content']

        return top_text

    def get_relevant_documents(self, search_phrase):
        """
        Fetches relevant documents from elastic search based on query.

        Get only the documents that have a score greater than the average score.

        input:
            search_phrase (string): string to search for in ES

        output:
            (dict): dictionary of fetched documents
        """
        #  get all scores for top 10K documents
        index = self.search_index + '/_search'
        score_payload = {'from': 0, 'size': 1000, \
                         'fields': '_score', \
                         'query': {'query_string': { \
                                   'query': search_phrase.encode('utf-8'), \
                                   'fields': ['Full text:']}}}
        score_response = json.loads(elastic.search(elastic.ES_URL, index, score_payload))

        # create list of scores with 0 excluded
        scores = []
        for i in score_response['hits']['hits']:
            float_score = float(i['_score'])
            if float_score > 0:
                scores.append(float_score)

        median_score = np.median(scores)
        quartile = np.percentile(scores, 75)

        # get responses where min_score >= median_score
        payload = {'min_score': quartile, \
                   'from': 0, 'size': 1000, \
                   'query': {'query_string': {'query': search_phrase.encode('utf-8'), \
                                              'fields': ['Full text:']}}}


        response = json.loads(elastic.search(elastic.ES_URL, index, payload))
        return response

def main():
    """
    Called when module is called from command line
    """
    ess = ElasticSentimentSelection('flattened-articles', 'Full Text:', 'googles', 'documentSentiment')
    print ess.get_best_sentence('Alexander Hamilton')

    # print 'Phrase: Alexander Hamilton, Polarity: ' + \
    #       str(ess.get_sentiment_for_phrase('Alexander Hamilton'))
    # print 'Phrase: Second City, Polarity: ' + \
    #       str(ess.get_sentiment_for_phrase('Second City'))
    # print 'Phrase: Chicago Style Theater, Polarity: ' + \
    #       str(ess.get_sentiment_for_phrase('Chicago Style Theater'))


if __name__ == '__main__':
    main()
