import unittest
import clean_data

class CleanDataTests(unittest.TestCase):
    def __get_sections(self):
        test_file = 'raw_data/ChrisJones-test.txt'
        return test_file

    def __get_articles(self):
        sections = clean_data.find_sections('raw_data/ChrisJones-test.txt')
        articles = clean_data.find_articles(sections)
        return articles

    def test_find_sections(self):
        sections = clean_data.find_sections('raw_data/ChrisJones-test.txt')
        NUM_SECTIONS = 5
        self.assertEquals(NUM_SECTIONS, len(sections))

    def test_find_article_sections(self):
        NUM_ARTICLES = 2
        articles = self.__get_articles()
        self.assertEquals(NUM_ARTICLES, len(articles))

    def test_split_article(self):
        article = self.__get_articles()[0]
        full_text, metadata = clean_data.split_article(article)
        self.assertNotEqual(0, len(metadata))
        self.assertNotEqual(0, len(full_text))

def main():
    """
    Called when module is called from command line
    """
    unittest.main()

if __name__ == '__main__':
  main()
