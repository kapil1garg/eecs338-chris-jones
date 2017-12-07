"""
This module is used to clean raw data retieved from Nexis
"""
import re
import os


def split_article(article):
    """
    Splits single article into full text and metadata

    input:
        article (string): single article from raw data

    outputs:
        (string): full text
        (string): metadata
    """
    metadata = []
    full_text = []
    hit_metadata = False
    regex = r'Title: '
    for line in article:
        if re.match(regex, line):
            hit_metadata = True
        if hit_metadata:
            metadata.append(line)
        else:
            full_text.append(line)

    return full_text, metadata


def write(lines, title):
    """
    Writes file to disk

    input:
        lines (list): individual lines in file to write
        title (string): file name
    """
    output_file = open(title, 'w+')
    for line in lines:
        output_file.write(line)
    output_file.close()


def write_article_to_file(article, index):
    """
    Parses out article from large file and exports file

    input:
        article (string): article text
        index (int): index of article loaded in
    """
    full_text, metadata = split_article(article)
    curpath = os.path.abspath(os.curdir)

    # check if output directories exist
    full_text_dirname = os.path.dirname(curpath + '/clean_data/full_text/')
    metadata_dirname = os.path.dirname(curpath + '/clean_data/metadata/')

    if not os.path.exists(full_text_dirname):
        os.makedirs(full_text_dirname)

    if not os.path.exists(metadata_dirname):
        os.makedirs(metadata_dirname)

    write(full_text, curpath + '/clean_data/full_text/' + index)
    write(metadata, curpath + '/clean_data/metadata/' + index)


def find_articles(sections):
    """
    Parses large file into sections

    input:
        sections (list): list of sections

    output:
        (list): articles parsed into list
    """
    regex = r'Document \d+ of \d+'
    articles = []
    for section in sections:
        if re.match(regex, section[1]):
            articles.append(section)
    return articles


def find_sections(file_name):
    """
    Parses different sections out

    input:
        file_name (string): file to parse sections from

    output:
        (list): list of parsed sections
    """
    input_file = open(file_name)
    text = input_file.readlines()

    break_text = '____________________________________________________________\r\n'

    current_section = []
    all_sections = []
    for line in text:
        if line != break_text:
            current_section.append(line)
        elif line == break_text:
            if len(current_section) > 0:
                all_sections.append(current_section)
                current_section = []
    all_sections.append(current_section)

    return all_sections


def write_file(file_name, i):
    """
    Parses sections and then calls file writer for text and metadata

    inputs:
        file_name (string): file to load in
        i (int): file index to be used as file name
    """
    sections = find_sections(file_name)
    articles = find_articles(sections)

    for j in range(0, len(articles)):
        index = str(i) + str(j) + '.txt'
        write_article_to_file(articles[j], index)


def main():
    """
    Called when module is called from command line
    """
    base_file_name = 'ChrisJones-'

    for i in range(0, 9):
        file_name = 'raw_data/' + base_file_name + str(i) + '.txt'
        write_file(file_name, i)


if __name__ == '__main__':
    main()
