"""
This module is used to find key words and phrases in the articles index and map the
text to sentiment values in the googles index
"""
import json
import re
import pickle
import math
import os
import numpy as np
import nltk
import elastic

class ElasticSentimentSelection(object):
    """
    Conducts a search on an index and then finds a matching document
    in another index where sentiment is kept by id match
    """
    def __init__(self, search_index, text_search_field, sentiment_index, sentiment_field, \
                 rebuild=False):
        # declare variables for sentiment searcher
        self.search_index = search_index
        self.text_search_field = text_search_field
        self.sentiment_index = sentiment_index
        self.sentiment_field = sentiment_field
        self.relevant_documents = {}

        # create sentiment model for objectivity
        self.word_features = []
        self.classifier = None

        if os.path.exists('models/sentiment/label_probdist.p') and \
           os.path.exists('models/sentiment/feature_probdist.p') and not rebuild:
            print 'loading sentiment model'

            # load in model files
            with open('models/sentiment/label_probdist.p', 'rb') as label_probdist_file:
                label_probdist = pickle.load(label_probdist_file)
            with open('models/sentiment/feature_probdist.p', 'rb') as feature_probdist_file:
                feature_probdist = pickle.load(feature_probdist_file)

            # instantiate classifier
            self.classifier = nltk.NaiveBayesClassifier(label_probdist, feature_probdist)
        else:
            print 'generating sentiment model'

            # get training data
            subjective_sents = nltk.corpus.subjectivity.sents(categories='subj')
            objective_sents = nltk.corpus.subjectivity.sents(categories='obj')

            subjective_docs = [(sent, 'subj') for sent in subjective_sents]
            objective_docs = [(sent, 'obj') for sent in objective_sents]

            # train model
            sentiment_training_data = subjective_docs + objective_docs
            self.classifier = self.train_sentiment_classifier(sentiment_training_data)

            # save out model so it will not need to be regenerated
            with open('models/sentiment/label_probdist.p', 'wb') as label_probdist_file:
                pickle.dump(self.classifier._label_probdist, label_probdist_file)
            with open('models/sentiment/feature_probdist.p', 'wb') as feature_probdist_file:
                pickle.dump(self.classifier._feature_probdist, feature_probdist_file)

    def extract_words(self, text_tuples):
        """
        Extraces all words from a training corpus where each entry is a tuple ([tokens], sentiment).

        Inputs:
            text_tuples (list of tuples): list of tuples in form ([tokens], sentiment)

        Output:
            (list): all words in training corpus
        """
        all_words = []
        for (words, _) in text_tuples:
            all_words.extend(words)
        return all_words

    def create_word_features(self, wordlist):
        """
        Returns the unique set of words from a wordlits

        Inputs:
            wordlist (list): list of string words

        Output:
            (list): unique words in wordlist
        """
        wordlist = nltk.FreqDist(wordlist)
        self.word_features = wordlist.keys()
        return self.word_features

    def extract_features(self, document):
        """
        Extracts features from a document given a wordlist

        Input:
            document (list): list of words in document

        Output:
            (list): features found in document
        """
        document_words = set(document)
        features = {}
        for word in self.word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    def train_sentiment_classifier(self, training_data):
        """
        Trains a Naive Bayes Classifier on a set of training data

        Inputs:
            training_data (list of tuples): list of tuples in format ([tokens], sentiment)

        Output:
            (NaiveBayesClassifier): instance of a trained naive bayes classifier
        """
        #  generate list of word features for training data
        self.create_word_features(self.extract_words(training_data))

        # extract features for training data
        training_set = nltk.classify.apply_features(self.extract_features, training_data)

        # create and return classifier
        return nltk.NaiveBayesClassifier.train(training_set)


    def get_avg_sentiment(self, search_phrase):
        """
        Computes average sentiment from all relevant documents returned from search.

        inputs:
            search_phrase (string): string to search for in ES

        output:
            (float): average polarity from all related documents
        """
        # get relevant documents
        self.relevant_documents = self.get_relevant_documents(search_phrase)

        # return average polarity for phrase
        average_polarity = 0
        for i in self.relevant_documents['hits']['hits']:
            average_polarity += float(i['_source']['documentSentiment']['polarity'])

        return average_polarity / (len(self.relevant_documents['hits']['hits']) + 0.0000001)

    def get_best_sentence(self, search_phrase):
        """
        Return best sentence for search phrase

        Inputs:
            search_phrase (string): string phrase to search for in elastic search

        Outputs:
            (string): top sentence found in best doc
            (article_title): title of article for context
        """
        # get sentiment for phrase
        average_sentiment = self.get_avg_sentiment(search_phrase)

        # find closest document
        closest_doc = self.get_closest_document(average_sentiment)

        # find the best (most subjective) sentence
        top_sentence = self.get_most_subjective_sentence(closest_doc)

        # get article title
        raw_title = closest_doc['_source']['ProQ:']
        article_title = re.split('title=', raw_title)[1].replace('+', ' ').replace('&', '')

        return top_sentence, article_title

    def get_closest_document(self, sentiment):
        """
        Returns closest document by sentiment to average sentiment.

        Inputs:
            sentiment (float): average sentiment of all relevant documents

        Outputs:
            (dictionary): closest document
        """
        closest = {}
        closest_value = 10000000

        for i in self.relevant_documents['hits']['hits']:
            current_diff = math.sqrt(math.pow(i['_source']['documentSentiment']['polarity'] - \
                                              sentiment, 2))

            if current_diff < closest_value:
                closest = i
                closest_value = current_diff

        return closest

    def get_most_subjective_sentence(self, closest_doc):
        """
        Compue subjectivity for each sentence and pick one that is most

        Inputs:
            closest_doc (dictionary): dictionary fetched from ES

        Outputs;
            (string): top sentence by subjectivity
        """
        top_sentence = ''
        top_sentence_subjectivity = 0

        for i in closest_doc['_source']['sentences']:
            curr_sentence_tokens = i['content'].split()
            curr_sentence_features = self.extract_features(curr_sentence_tokens)
            curr_subjectivity = self.classifier.prob_classify(curr_sentence_features).prob('subj')

            if curr_subjectivity > top_sentence_subjectivity:
                top_sentence_subjectivity = curr_subjectivity
                top_sentence = i['content']

        return top_sentence

    def get_relevant_documents(self, search_phrase):
        """
        Fetches relevant documents from elastic search based on query.

        Get only the documents that have a score greater than the average score.

        input:
            search_phrase (string): string to search for in ES

        output:
            (dict): dictionary of fetched documents
        """
        #  get all scores for top 100 documents
        index = self.search_index + '/_search'
        score_payload = {'from': 0, 'size': 500, \
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

        quartile = np.percentile(scores, 50)

        # get responses where min_score >= quartile
        payload = {'_source': ['ProQ:', 'sentences', 'documentSentiment'],
                   'min_score': quartile, \
                   'from': 0, 'size': 500, \
                   'query': {'query_string': {'query': search_phrase.encode('utf-8'), \
                                              'fields': ['Full text:']}}}


        response = json.loads(elastic.search(elastic.ES_URL, index, payload))
        return response

def main():
    """
    Called when module is called from command line
    """
    ess = ElasticSentimentSelection('flattened-articles', 'Full Text:', \
                                    'googles', 'documentSentiment')
    print ess.get_best_sentence('Aladdin')
    print ess.get_best_sentence('Romeo and Juliet')
    print ess.get_best_sentence('Hamlet')

if __name__ == '__main__':
    main()
