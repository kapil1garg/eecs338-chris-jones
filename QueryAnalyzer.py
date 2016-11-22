from google_nlp_api import GoogleNlp
import pdb

class QueryAnalyzer:
  """
    Analyzes queries from slackbot
  """

  def __init__(self):
    self.google_nlp = GoogleNlp()
    self.genres = ['comedy', 'drama', 'tragedy', 'satire', 'farce', 'musicals']
    with open('data/theaters.txt', 'r') as theater_file:
      self.theaters = theater_file.read().splitlines()

  def get_entities(self, query):
    """
      Finds the entites of the input query

      input:
        query (string): The query to be anylyzed

      return:
        entites (list of strings): List of entities in query
    """
    return_blob = self.google_nlp.analyze_entities(query)
    entities = []
    for entity in return_blob['entities']:
      entities.append(entity['name'])
    return entities

  def get_subject(self, query):
    """
      Finds the noun subject of the input query

      input:
        query (string): The query to be anylyzed

      return:
        (string) || None: Noun subject of query
    """
    return_blob = self.google_nlp.analyze_syntax(query)
    for token in return_blob['tokens']:
      if token['dependencyEdge']['label'] == "NSUBJ":
        return token['text']['content']

  def analyze_dependencies(self, query):
    print "Not yet implemented"

  def annotate_query(self, query):
    print "Not yet implemented"

  def get_keywords(self, query):
    return_blob = self.google_nlp.analyze_syntax(query)
    keywords = {'keywords': {'NOUN': [], 'VERB': []}, 'edges': {'ROOT': [], 'NSUBJ': [], 'POBJ': [], 'ATTR': []}}
    for token in return_blob['tokens']:
      if token['partOfSpeech']['tag'] in keywords['keywords'].keys():
        keywords['keywords'][token['partOfSpeech']['tag']].append(token['text']['content'])
      if token['dependencyEdge']['label'] in keywords['edges'].keys():
        keywords['edges'][token['dependencyEdge']['label']].append(token['text']['content' ])
    return keywords

  def get_framework(self, query, keywords):
    for t in self.theaters:
      print t
      query = query.replace(t, 'THEATER')
    for g in self.genres:
      query = query.replace(g, 'GENRE')
    # for n in keywords['keywords']['NOUN']:
    #   query = query.replace(n, 'NOUN')
    return query


# class AnnotatedQuery:
#   def __init__(self, ):


if __name__ == '__main__':
  a = QueryAnalyzer()
  q = 'How has the Goodman Theatre changed over time?'
  k = a.get_keywords(q)
  print a.get_framework(q, k)
