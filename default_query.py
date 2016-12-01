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

    def format_response(self, result_tuple):

        article_title = self.clean_article_title(result_tuple[1])

        # Grab sentence from query
        sent = result_tuple[0]['hits'][0]['_source']['content']
        # Split full text into paragraphs
        article_text = result_tuple[2].splitlines()
        # Find the paragraph with the sentence we want
        response_text = article_text[0] #pick first paragraph as default
        for p in article_text:
            if re.search(sent, p) != None:
                # Add markup formatting
                response_text = p.replace(sent, '*{}*'.format(sent))
                print 'found'
                break
        # Construct and Return response to slackbot
        return '{0}\n_From: {1}_'.format(response_text.encode('utf8'), article_title)



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

        return self.format_response(r[0])





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

        return self.format_response(r[0])


    def generate_response_good_noun(self, query, annotated_query):
        payload = {
            "_source": ["sentences.content", "Full text:", "ProQ:"],
            "query": {
                "bool": {
                    "must": [{
                        "match": {
                            "Full text:": p
                        }}
                             for p in annotated_query.people]
                }
            }
        }

        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        ids = [i['_id'] for i in r]

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
                                         "must": [{"match": {"sentences.content": p}} for p in annotated_query.people + annotated_query.keywords['keywords']['NOUN']]

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

    def generate_response_favorite_person(self, query, annotated_query):
        ids = self.get_relevant_document_ids(query)

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


                                         [ {"match": {"sentences.content": i}} for i in ['favorite', 'outstanding', 'terrific', 'killer', 'best', 'precious', 'dearest', 'greatest']],
                                         "must": [{"match": {"sentences.content": p}} for p in annotated_query.keywords['keywords']['NOUN']]

                                     }
                                 },
                                 "inner_hits": {}
                             }}]
                }
            }
        }
        r = json.loads(elastic.search(elastic.ES_URL, '/flattened-articles/_search', payload))['hits']['hits']
        r = [(i['inner_hits']['sentences']['hits'], i['_source']['ProQ:'], i['_source']['Full text:']) for i in r]

        print 'Favorite {}'.format(annotated_query.keywords['keywords']['NOUN'][0])
        return self.format_response(r[0])

class LocationQuery(DefaultQuery):
    def __init__(self):
        self.dummy = 0
    def ny_v_chicago(self, query, annotated_query):
        t = "Acting ensembles are more common in Chicago than any other major theater city. *In New York, actors tend to be viewed as a commodity.* And unless they have celebrity status, actors there don't have a great deal of influence over play selection at the city's non-profit theaters, which are mostly led by auteur artistic directors. It's much the same in London. And with a few exceptions -- the Milwaukee Repertory Theater being one -- most American regional theaters don't keep a company of actors. They hire performers by the show. Actors don't get to pick roles for themselves.\nBut in Chicago -- where actors enjoy more power -- the storied acting ensemble is common.\nIt defines the Steppenwolf Theatre Company -- a theater that, in its early days, often picked its repertoire based on a talented someone's desire for a juicy role. The recent Lookingglass Theatre production of \"Our Town\" was specifically designed to showcase the intertwined, creative relationships of its ensemble. Many smaller theaters -- Congo Square, Lifeline, Profiles and many others -- have acting ensembles."
        s = "_From: Pondering the ensemble question_"
        return "{0}\n{1}".format(t, s)
    def chicago_essence(self, query, annotated_query):
        t = "Galati adapting an iconic American work by John Steinbeck inevitably recalls one of the most famous productions in the history of Chicago theater, \"The Grapes of Wrath,\" which in 1988 showcased the Dust Bowl work of such actors as Gary Sinise, Lois Smith and John C. Reilly and did a great deal to cement Steppenwolf's international reputation (although in his Tribune review, then-critic Richard Christiansen expressed disappointment). *\"The Grapes of Wrath\" had a formidable life, moving to Broadway in 1990 and becoming, in many minds, one of that small collection of shows to embody the very essence of Steppenwolf.*"
        s = "_From: Galati returns with East of Eden adaptation_"
        return "{0}\n{1}".format(t, s)

