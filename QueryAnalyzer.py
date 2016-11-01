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
