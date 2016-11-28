from google_nlp_api import GoogleNlp
import pdb
import re

class QueryAnalyzer:
  """
    Analyzes queries from slackbot
  """

  def __init__(self):
    self.google_nlp = GoogleNlp()
    self.genres = ['comedy', 'drama', 'tragedy', 'satire', 'farce', 'musicals', 'musical']
    with open('data/theaters.txt', 'r') as theater_file:
      self.theaters = theater_file.read().splitlines()
    with open('data/people.txt', 'r') as people_file:
      self.people = people_file.read().splitlines()
    with open('data/shows.txt', 'r') as shows_file:
      self.shows = shows_file.read().splitlines()

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

  def get_keywords(self, query):
    return_blob = self.google_nlp.analyze_syntax(query)

  def get_framework(self, query, keywords):
    for t in self.theaters:
      query = query.replace(t, 'THEATER')
    for g in self.genres:
      query = query.replace(g, 'GENRE')
    # for n in keywords['keywords']['NOUN']:
    #   query = query.replace(n, 'NOUN')
    return query

  def annotate(self, query):
    return AnnotatedQuery(query, self.shows, self.theaters, self.people)


class AnnotatedQuery:
  """
  Helper class to get clean up syntax when working with query annotations

  args:
    query (string): the text query to annotate with the Google Natural Language API
    shows (list): the list of shows (strings)
    theaters (list): the list of theaters (strings)
    people (list): the list of people (strings)

  """
  def __init__(self, query, shows, theaters, people):
    self.api_client = GoogleNlp()
    self.api_results = self.api_client.annotate_text(query)
    self.keywords = {'keywords': {'NOUN': [], 'VERB': []}, 'edges': {'ROOT': [], 'NSUBJ': [], 'POBJ': [], 'ATTR': []}}
    for token in self.api_results['tokens']:
      if token['partOfSpeech']['tag'] in self.keywords['keywords'].keys():
        self.keywords['keywords'][token['partOfSpeech']['tag']].append(token['text']['content'])
      if token['dependencyEdge']['label'] in self.keywords['edges'].keys():
        self.keywords['edges'][token['dependencyEdge']['label']].append(token['text']['content' ])
    self.shows = []
    self.theaters = []
    self.people = []
    for s in shows:
      if re.search(s, query) != None:
        self.shows.append(s)
    for t in theaters:
      if re.search(t, query) != None:
        self.theaters.append(t)
    for p in people:
      if re.search(p, query) != None:
        self.people.append(p)


if __name__ == '__main__':
  a = QueryAnalyzer()
  q = 'How has the Goodman Theatre changed over time?'
  k = a.get_keywords(q)
  print a.get_framework(q, k)
