"""
This module is used to annotate text using the GoogleNLP API
"""
import argparse
import httplib2
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

# Notes to self
# pip install --upgrade google-api-python-client
# set up application default credentials in GOOGLE_APPLICATION_CREDENTIALS

DISCOVERY_URL = ('https://{api}.googleapis.com/'
                 '$discovery/rest?version={apiVersion}')
ENCODING_TYPE = 'UTF32'

class GoogleNlp(object):
    """
    This class is a wrapper for the Google Natural Language API. Authentication
    is handled using the recommended Application Default Credentials.

    Todo:
        * Pick and adhere to a consistent style
    """
    def __init__(self):
        # Authenticate (boilerplate stuff from the API docs)
        self.http = httplib2.Http()
        self.credentials = GoogleCredentials.get_application_default().create_scoped(
            ['https://www.googleapis.com/auth/cloud-platform'])
        self.credentials.authorize(self.http)
        self.service = discovery.build('language',
                                       'v1beta1',
                                       http=self.http,
                                       discoveryServiceUrl=DISCOVERY_URL)

    def analyze_sentiment(self, text_string):
        """
        Run sentiment analysis on text from a string using the Google
        natural language API

        args:
            text_string (string): a text string to be analyzed
        """
        service_request = self.service.documents().analyzeSentiment(
            body={
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': text_string
                }
            }
        )
        response = service_request.execute()
        return response

    def analyze_entities(self, text_string):
        """
        Run entity extraction on text from a string using the Google
        natural language API

        args:
            text_string (string): a text string to be analyzed
        """
        service_request = self.service.documents().analyzeEntities(
            body={
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': text_string
                },
                'encodingType': ENCODING_TYPE
            }
        )
        response = service_request.execute()
        return response

    def analyze_syntax(self, text_string):
        """
        Run entity extraction on text from a string using the Google
        natural language API

        args:
            text_string (string): a text string to be analyzed
        """
        service_request = self.service.documents().annotateText(
            body={
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': text_string
                },
                'features': {
                    'extractSyntax': True,
                },
                'encodingType': ENCODING_TYPE
            }
        )
        response = service_request.execute()
        return response

    def annotate_text(self, text_string, extract_syntax=True, extract_entities=True, \
                      extract_sentiment=True):
        """
        Run entity extraction on text from a string using the Google
        natural language API

        args:
            text_string (string): a text string to be analyzed
            extract_syntax (boolean): Extract syntax information?
                default = True
            extract_entities (boolean): Extract entities?
                default = True
            extract_sentiment (boolean): Extract sentiment for the whole document?
                default = True
        """
        service_request = self.service.documents().annotateText(
            body={
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': text_string
                },
                'features': {
                    'extractSyntax': extract_syntax,
                    'extractEntities': extract_entities,
                    'extractDocumentSentiment': extract_sentiment
                },
                'encodingType': ENCODING_TYPE
            }
        )
        response = service_request.execute()
        return response



    def analyze_sentiment_file(self, text_file):
        """
        Run sentiment analysis on text from a file using the Google
        natural language API

        args:
            text_file (string) : a file path to the text file to be analyzed
        """
        with open(text_file, 'r') as input_file:
            return self.analyze_sentiment(input_file.read())

    def analyze_entities_file(self, text_file):
        """
        Run entity extraction on text from a file using the Google
        natural language API

        args:
            text_file (string): a file path to the text file to be analyzed
        """
        with open(text_file, 'r') as input_file:
            return self.analyze_entities(input_file.read())

    def annotate_text_file(self, text_file, extract_syntax=True, extract_entities=True, \
                           extract_sentiment=True):
        """
        Run entity extraction on text from a file using the Google
        natural language API

        args:
            text_file (string): a file path to the text file to be analyzed
            extract_syntax (boolean): Extract syntax information?
                default = True
            extract_entities (boolean): Extract entities?
                default = True
            extract_sentiment (boolean): Extract sentiment for the whole document?
                default = True
        """
        with open(text_file, 'r') as input_file:
            return self.annotate_text(input_file.read(),
                                      extract_syntax=extract_syntax,
                                      extract_entities=extract_entities,
                                      extract_sentiment=extract_sentiment)

def main():
    """
    Called when module is called from command line
    """
    # Simple Demo:
    # take text file from the commandline and return all the possible data from the API
    parser = argparse.ArgumentParser()
    parser.add_argument('text_file', help='The path to the file you wish to analyze')
    args = parser.parse_args()
    google_nlp = GoogleNlp()

    print google_nlp.analyze_sentiment_file(args.text_file)
    print google_nlp.analyze_entities_file(args.text_file)
    print google_nlp.annotate_text_file(args.text_file)

if __name__ == '__main__':
    main()
