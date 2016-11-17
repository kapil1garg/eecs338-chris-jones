from google_nlp_api import GoogleNlp
import pdb

class QueryAnalyzer:
  """
    Analyzes queries from slackbot
  """

  def __init__(self):
    self.google_nlp = GoogleNlp()

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
    for g in ['comedy', 'drama', 'tragedy', 'satire', 'farce', 'musicals']:
      query = query.replace(g, 'GENRE')
    for n in keywords['keywords']['NOUN']:
      query = query.replace(n, 'NOUN')
    return query

if __name__ == '__main__':
  a = QueryAnalyzer()
  print 'Keywords: ', a.get_keywords('What did you think of the acting in Hamilton?')
