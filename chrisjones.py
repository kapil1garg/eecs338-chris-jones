import requests
import json
import elastic



class ChrisJones:
    def __init__(self):
        # Do ES auth stuff
        print 'ChrisJones activated'

    def respond(self, query):
        # determine question type
        # then generate appropriate response

        print query
        # for now, just return the same stuff all the time
        payload = {"query": {"query_string": {"query": query.encode('utf-8'),
                                          "fields": ["Full text:"]}}}
        print payload
        response = elastic.search(elastic.ES_URL, '_search', payload)
        response = json.loads(response)

        hits = response['hits']['hits']
        max_score = response['hits']['max_score']


        for a in hits:
            if a["_score"] == max_score:
                return a["_source"]['Full text:']

        return response





if __name__ == '__main__':
    query = 'alexander hamilton'
    payload = {"query": {"query_string": {"query": query,
                                          "fields": ["Full text:"]}}}
    r = requests.post('http://localhost:9200/' + '_search', data = json.dumps(payload))
    print(r.text)
