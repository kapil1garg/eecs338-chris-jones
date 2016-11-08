"""
This module is used to upload combined parsed full text, metadata, and google annotations to ES.
"""
import os
import json
import elastic
import more_parsing as mp

class AnnotatedArticlesUploader(object):
    """Class to quickly upload annotated documents to elastic search"""
    def __init__(self, url, index, doc_type, fulltext, metadata, google_results, \
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

    def upload_to_es(self):
        """
        Loops through each file, loads in dictionaries, combines, and uploads to elastic search
        """
        counter = 0
        for i in self.fulltext:
            # check if corresponding file number can be found in each set
            if i in self.metadata and i in self.google_results:
                payload = self.combine_data(self.load_fulltext(i), self.load_metadata(i), \
                                            self.load_annotations(i))

                elastic.upload(self.url, self.index, self.doc_type, str(counter), payload)
                counter += 1

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

    aauploader = AnnotatedArticlesUploader(elastic.ES_URL, \
                                         'annotated-articles', 'annotated-article', \
                                         full_text, metadata, google_annotations, keys, \
                                         full_text_dir, metadata_dir, google_annotations_dir)
    aauploader.upload_to_es()

if __name__ == '__main__':
    main()
