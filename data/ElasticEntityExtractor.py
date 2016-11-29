"""
This module is used to extract entities from Elastic Search annoted by the Google NLP API
"""
import json
import os
import sys
sys.path.append(os.path.join('..'))

import elastic

SHOW_QUERY = {
    'from': 0,
    'size': 10000,
    '_source': ['inner_hits'],
    'query': {
        'nested': {
            'path': 'entities',
            'filter': {
                'bool': {
                    'must': [{
                        'match': {
                            'entities.type': 'WORK_OF_ART'
                        }
                    }]
                }
            },
            'inner_hits': {
                '_source': ['name']
            }
        }
    }
}

PEOPLE_QUERY = {
    'from': 0,
    'size': 10000,
    '_source': ['inner_hits'],
    'query': {
        'nested': {
            'path': 'entities',
            'filter': {
                'bool': {
                    'must': [{
                        'match': {
                            'entities.type': 'PEOPLE'
                        }
                    }]
                }
            },
            'inner_hits': {
                '_source': ['name']
            }
        }
    }
}

THEATER_QUERY = {
    'from': 0,
    'size': 10000,
    '_source': ['inner_hits'],
    'query': {
        'nested': {
            'path': 'entities',
            'filter': {
                'bool': {
                    'should': [{
                        'match': {
                            'entities.type': 'ORGANIZATION'
                        }
                    }, {
                        'match': {
                            'entities.type': 'LOCATION'
                        }
                    }]
                }
            },
            'inner_hits': {
                '_source': ['name', 'type']
            }
        }
    }
}

class ElasticEntityExtractor(object):
    """Extracts entities stored in Elastic Search annotated by the Google NLP API and saves to disk"""
    def __init__(self, show_file, people_file, theater_file):
        # files to pull existing data and store new parsed data
        self.show_file = show_file
        self.people_file = people_file
        self.theater_file = theater_file

        # sets to hold unique entities for each type above
        self.show_entities = set()
        self.people_entities = set()
        self.theater_entities = set()

        # read in existing entites
        self.__load_existing_data()

    def __load_existing_data(self):
        """
        Loads data from file if file exists
        """
        if os.path.exists(self.show_file):
            self.__load_data_for_type('show')
        if os.path.exists(self.people_file):
            self.__load_data_for_type('people')
        if os.path.exists(self.theater_file):
            self.__load_data_for_type('theater')

    def __load_data_for_type(self, entity_type):
        """
        Load data for specific entity_type/file

        Input:
            entity_type (string): entity type to fetch data for
        """
        if entity_type == 'show':
            with open(self.show_file, 'rb') as show_file:
                self.show_entities = set(show_file.read().splitlines())
        elif entity_type == 'people':
            with open(self.people_file, 'rb') as people_file:
                self.people_entities = set(people_file.read().splitlines())
        elif entity_type == 'theater':
            with open(self.theater_file, 'rb') as theater_file:
                self.theater_entities = set(theater_file.read().splitlines())

    def get_entities_for_type(self, entity_type, overwrite=False):
        """
        Gets entites for specific entity_type from elastic search

        Inputs:
            entity_type (string): entity type to look for
            overwrite (bool): overwrite file on disk
        """
        index = 'flattened-articles/_search'
        if entity_type == 'show':
            elastic_response = json.loads(elastic.search(elastic.ES_URL, index, SHOW_QUERY))
        elif entity_type == 'people':
            elastic_response = json.loads(elastic.search(elastic.ES_URL, index, PEOPLE_QUERY))
        elif entity_type == 'theater':
            elastic_response = json.loads(elastic.search(elastic.ES_URL, index, THEATER_QUERY))

        for i in elastic_response['hits']['hits']:
            for j in i['inner_hits']['entities']['hits']['hits']:
                curr_name = j['_source']['name']

                if entity_type == 'show':
                    self.show_entities.add(curr_name)
                elif entity_type == 'people':
                    self.people_entities.add(curr_name)
                elif entity_type == 'theater':
                    if 'theater' in curr_name.lower():
                        self.theater_entities.add(curr_name)

        if overwrite:
            if entity_type == 'show':
                self.save_entities(self.show_entities, self.show_file)
            elif entity_type == 'people':
                self.save_entities(self.people_entities, self.people_file)
            elif entity_type == 'theater':
                self.save_entities(self.theater_entities, self.theater_file)


    def get_all_entities(self, overwrite=False):
        """
        Gets entites for all types from elastic search

        Inputs:
            type (string): entity type to look for
            overwrite (bool): overwrite file on disk
        """
        self.get_entities_for_type('show', overwrite=overwrite)
        self.get_entities_for_type('people', overwrite=overwrite)
        self.get_entities_for_type('theater', overwrite=overwrite)

    def save_entities(self, entities, filename):
        """
        Saves entities to given filename

        Inputs:
            entities (set): unique set of entities to export
            filename (string): file to write to
        """
        with open(filename, 'wb') as output_file:
            sorted_entities = list(entities)
            sorted_entities.sort()

            for item in sorted_entities:
                output_file.write(item + '\n')

def main():
    """
    Called when module is called from command line
    """
    show_file = 'shows.txt'
    people_file = 'people.txt'
    theater_file = 'theaters.txt'

    eee = ElasticEntityExtractor(show_file, people_file, theater_file)
    eee.get_all_entities(overwrite=True)

if __name__ == '__main__':
    main()
