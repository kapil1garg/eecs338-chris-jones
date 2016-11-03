import requests
import json
import elastic
from google_nlp_api import GoogleNlp
import re



class ChrisJones:
    def __init__(self):
        # Do ES auth stuff
        print 'ChrisJones activated'

    def respond(self, query):
        # determine question type
        # then generate appropriate response

        # print query

        a = GoogleNlp()
        annotated_query = a.annotate_text(query)
        print annotated_query


        # for now, just return the same stuff all the time
        payload = {"query": {"query_string": {"query": query.encode('utf-8'),
                                          "fields": ["Full text:"]}}}
        response = elastic.search(elastic.ES_URL, 'articles/_search', payload)
        response = json.loads(response)

        hits = response['hits']['hits']
        max_score = response['hits']['max_score']


        for a in hits:
            if a["_score"] == max_score:
                match_id = a["_id"]
                # return a["_source"]['Full text:']

        payload = {"query": {"ids": {"values": [match_id]}}}
        annotated_article = elastic.search(elastic.ES_URL, 'googles/_search', payload)
        annotated_article = json.loads(annotated_article)
        sentences = annotated_article['hits']['hits'][0]['_source']['sentences']
        sentences = [i['text']['content'] for i in sentences]
        sentences = [i for i in sentences if re.search('Hamilton', i) != None]
        return sentences[len(sentences) - 2]





if __name__ == '__main__':
    query = 'alexander hamilton'
    payload = {"query": {"query_string": {"query": query,
                                          "fields": ["Full text:"]}}}
    r = requests.post('http://localhost:9200/' + '_search', data = json.dumps(payload))
    print(r.text)
