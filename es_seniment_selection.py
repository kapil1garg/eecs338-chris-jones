"""
This module is used to find key words and phrases in the articles index and map the
text to sentiment values in the googles index
"""
import json
import elastic


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

    def get_sentiment_for_phrase(self, search_phrase):
        # get relevant documents
        relevant_documents = self.get_relevant_documents(search_phrase)

        # find all indicies where score >= 0.8
        indicies = []
        for i in relevant_documents['hits']['hits']:
            indicies.append(i['_id'])

        # find corresponding sentiment documents
        document_sentiments = self.get_document_sentiment(indicies)

        # return average polarity for phrase
        average_polarity = 0
        for i in document_sentiments:
            average_polarity += float(document_sentiments[i]['polarity'])

        return average_polarity / (len(document_sentiments.keys()) + 0.0000001)


    def get_relevant_documents(self, search_phrase):
        """
        Fetches relevant documents from elastic search based on query
        """
        payload = {'query': {'query_string': {'query': search_phrase.encode('utf-8'),
                                          'fields': ['Full text:']}}}

        index = self.search_index + '/_search'
        response = json.loads(elastic.search(elastic.ES_URL, index, payload))
        return response

    def get_document_sentiment(self, indicies):
        """
        Fetches sentiments for previously searched for documents
        """
        # query elastic search
        payload = {'query': {'ids': {'values': indicies}}}

        index = self.sentiment_index + '/_search'
        response = json.loads(elastic.search(elastic.ES_URL, index, payload))

        # parse into dictionary
        sentiment_dict = dict()

        for i in response['hits']['hits']:
            sentiment_dict[i['_id']] = i['_source'][self.sentiment_field]

        return sentiment_dict

def main():
    ess = ElasticSentimentSelection('articles', 'Full Text:', 'googles', 'documentSentiment')
    print 'Phrase: Alexander Hamilton, Polarity: ' + \
          str(ess.get_sentiment_for_phrase('Alexander Hamilton'))
    print 'Phrase: Second City, Polarity: ' + \
          str(ess.get_sentiment_for_phrase('Second City'))
    print 'Phrase: Chicago Style Theater, Polarity: ' + \
          str(ess.get_sentiment_for_phrase('Chicago Style Theater'))


if __name__ == '__main__':
    main()
