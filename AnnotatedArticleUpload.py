"""
This module is used to upload combined parsed full text, metadata, and google annotations to ES.
"""
import os
import json
import copy
import elastic
import more_parsing as mp

import pathos.pools as pp
from tqdm import tqdm


class AnnotatedArticlesUploader(object):
    """Class to quickly upload annotated documents to elastic search"""
    def __init__(self, url, index, doc_type, fulltext, metadata, google_results,
                 keys, fulltext_dir, metadata_dir, google_results_dir):
        """
        inputs:
            url (string): elastic search url
            index (string): index of ES to upload to
            doc_type (string): doc type of ES index to upload to
            fulltext (set of strings): files containing cleaned full text
            metadata (set of strings): files containing cleaned meta data
            google_results (set of strings): files containing annotations from google
            keys (list): keys to ignore when parsing
            fulltext_dir (string): directory containing full texts
            metadata_dir (string): directory containing meta data
            google_results_dir (string): directory containing google annotations
        """
        self.url = url
        self.index = index
        self.doc_type = doc_type
        self.fulltext = fulltext
        self.metadata = metadata
        self.google_results = google_results
        self.keys = keys
        self.fulltext_dir = fulltext_dir
        self.metadata_dir = metadata_dir
        self.google_results_dir = google_results_dir
        self.file_indices = dict(zip(list(self.fulltext), range(len(self.fulltext))))

    def combine_data(self, fulltext_dict, metadata_dict, google_results_dict):
        """
        Combines data dictionaries of fulltext, metadata, and google results into singular dict

        inputs:
            fulltext_dict (dict): parsed fulltext file
            metadata_dict (dict): parsed metadata file
            google_results_dict (dict): parsed google_results

        output:
            (dict): combined dictionary
        """
        # create combined dict with metadata as a separate key
        combined_dict = {}
        combined_dict['metadata'] = metadata_dict

        # combine dictionaries
        combined_dict.update(fulltext_dict)
        combined_dict.update(google_results_dict)

        return combined_dict

    def load_fulltext(self, file_name):
        """
        Loads in full text dictionary

        inputs:
            file_name (string): filename of full text data

        output:
            (dict): parsed dictionary of full text data
        """
        return mp.parse_document(self.fulltext_dir + file_name, self.keys)

    def load_metadata(self, file_name):
        """
        Loads in metadata dictionary

        inputs:
            file_name (string): filename of meta data

        output:
            (dict): parsed dictionary of meta data
        """
        return mp.parse_metadata(self.metadata_dir + file_name)

    def load_annotations(self, file_name):
        """
        Loads in google annotations dictionary

        inputs:
            file_name (string): filename of annotation data

        output:
            (dict): parsed dictionary of annotation data
        """
        output = {}
        with open(self.google_results_dir + file_name) as data_file:
            output = json.load(data_file)

        return output

    def reindex_features(self, combined_dict):
        """
        Flattens sentences, tokens, and entities structure to allow for nested querying

        input:
            combined_dict (dict): dictionary of combined full text, metadata, and google annotations

        output:
            (dict): combined_dict with reindexed features
        """
        # make a deep copy of combined dict to output
        output_dict = copy.deepcopy(combined_dict)

        # replace sentences
        sentence_count = len(output_dict['sentences'])
        new_sentence_list = [{} for x in xrange(sentence_count)]

        for i in xrange(sentence_count):
            current_sentence = output_dict['sentences'][i]
            new_sentence = {
                'content': current_sentence['text']['content'],
                'offset': current_sentence['text']['beginOffset']
            }
            new_sentence_list[i] = new_sentence

        output_dict['sentences'] = new_sentence_list

        # replace tokens
        token_count = len(output_dict['tokens'])
        new_token_list = [{} for x in xrange(token_count)]

        for i in xrange(token_count):
            current_token = output_dict['tokens'][i]
            new_token = {
                'content': current_token['text']['content'],
                'offset': current_token['text']['beginOffset'],
                'partOfSpeech': current_token['partOfSpeech']['tag'],
                'dependencyEdgeIndex': current_token['dependencyEdge']['headTokenIndex'],
                'dependencyEdgeLabel': current_token['dependencyEdge']['label'],
                'lemma': current_token['lemma']
            }

            new_token_list[i] = new_token

        output_dict['tokens'] = new_token_list

        # replace entities
        entity_count = len(output_dict['entities'])
        new_entity_list = [{} for x in xrange(entity_count)]
        master_mention_list = []

        for i in xrange(entity_count):
            #  parse out entities
            current_entity = output_dict['entities'][i]
            new_entity = {
                'metadata': current_entity['metadata'],
                'name': current_entity['name'],
                'salience': current_entity['salience'],
                'type': current_entity['type']
            }

            new_entity_list[i] = new_entity

            # parse out mentions
            mention_count = len(current_entity['mentions'])
            new_mention_list = [{} for x in xrange(mention_count)]

            for j in xrange(mention_count):
                current_mention = current_entity['mentions'][j]
                new_mention = {
                    'content': current_mention['text']['content'],
                    'offset': current_mention['text']['beginOffset'],
                    'entityName': current_entity['name']
                }

                new_mention_list[j] = new_mention

            master_mention_list += new_mention_list

        output_dict['entities'] = new_entity_list
        output_dict['mentions'] = master_mention_list

        return output_dict

    def upload_to_es(self, reindex_nested_features=False):
        """
        Loops through each file, loads in dictionaries, combines, and uploads to elastic search

        inputs:
            reindex_nested_features (bool): optional boolean to reindex features for nested search
        """
        # start multithreading pool
        processors = 4
        pool = pp.ProcessPool(processors)
        r = list(tqdm(pool.imap(self.upload_single_file_with_reindex, self.fulltext),
                      total=len(self.fulltext)))

        pool.close()
        pool.join()

    def upload_single_file_with_reindex(self, file):
        # check if corresponding file number can be found in each set
        if file in self.metadata and file in self.google_results:
            payload = self.combine_data(self.load_fulltext(file), self.load_metadata(file),
                                        self.load_annotations(file))

            # reindex features
            payload = self.reindex_features(payload)

            elastic.upload(self.url, self.index, self.doc_type, str(self.file_indices[file]), payload)

    def upload_single_file(self, file):
        # check if corresponding file number can be found in each set
        if file in self.metadata and file in self.google_results:
            payload = self.combine_data(self.load_fulltext(file), self.load_metadata(file),
                                        self.load_annotations(file))

            elastic.upload(self.url, self.index, self.doc_type, str(self.file_indices[file]), payload)


def main():
    """
    Method to run on call from command line
    """
    keys = mp.get_possible_keys(mp.PATH_TO_KEYS)
    full_text_dir = 'data/clean_data/full_text/'
    metadata_dir = 'data/clean_data/metadata/'
    google_annotations_dir = 'data/google_results/'

    full_text = set([x for x in os.listdir(full_text_dir) if x.endswith('.txt')])
    metadata = set([x for x in os.listdir(metadata_dir) if x.endswith('.txt')])
    google_annotations = set([x for x in os.listdir(google_annotations_dir) if x.endswith('.txt')])

    aauploader = AnnotatedArticlesUploader(elastic.ES_URL,
                                           'flattened-articles', 'flattened-article',
                                           full_text, metadata, google_annotations, keys,
                                           full_text_dir, metadata_dir, google_annotations_dir)
    aauploader.upload_to_es(reindex_nested_features=True)


if __name__ == '__main__':
    main()
