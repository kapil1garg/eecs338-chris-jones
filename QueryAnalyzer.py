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

  def annotate(self, query):
    """
    Return an AnnotatedQuery object for the given query

    args:
      query (string): the query you wish to annotate
    """
    return AnnotatedQuery(query, self.shows, self.theaters, self.people, self.genres)



class AnnotatedQuery:
  """
  Helper class to get clean up syntax when working with query annotations

  args:
    query (string): the text query to annotate with the Google Natural Language API
    shows (list): the list of shows (strings)
    theaters (list): the list of theaters (strings)
    people (list): the list of people (strings)
    genres (list): the list of genres (strings)

  """
  def __init__(self, query, shows, theaters, people, genres):
    self.api_client = GoogleNlp()
    self.query = query
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
    self.genres = []
    for s in shows:
      if re.search(s, query) != None:
        self.shows.append(s)
    for t in theaters:
      if re.search(t, query) != None:
        self.theaters.append(t)
    for p in people:
      if re.search(p, query) != None:
        self.people.append(p)
    for g in genres:
      if re.search(g, query) != None:
        self.genres.append(g)

  def get_framework(self):
    q = self.query
    for s in self.shows:
      q = q.replace(s, 'SHOW')
    for t in self.theaters:
      q = q.replace(t, 'THEATER')
    for p in self.people:
      q = q.replace(p, 'PERSON')
    for g in self.genres:
      q = q.replace(g, 'GENRE')
    print q
    for n in self.keywords['keywords']['NOUN']:
      q = q.replace(n, 'NOUN')
    return q



if __name__ == '__main__':
  a = QueryAnalyzer()
  q = 'How has the Goodman Theatre changed over time?'
  k = a.get_keywords(q)
  print a.get_framework(q, k)
