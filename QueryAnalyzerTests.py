import unittest
from QueryAnalyzer import QueryAnalyzer 

class QueryAnalyzerTests(unittest.TestCase):
  def test_find_entities(self):
    sentence = "Is Hamilton is a great play at the Chicago Theatre?"
    qa = QueryAnalyzer()
    entities = qa.get_entities(sentence)
    self.assertEqual(entities, ["Hamilton", "Chicago Theatre"])

  def test_find_subject(self):
    sentence = "Is Hamilton is a great play at the Chicago Theatre?"
    qa = QueryAnalyzer()
    subject = qa.get_subject(sentence)
    self.assertEqual(subject, "Hamilton")

def main():
  unittest.main()

if __name__ == '__main__':
  main()
