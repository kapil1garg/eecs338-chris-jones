import re


def split_article(article):
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
  f = open(title, 'w')
  for line in lines:
    f.write(line)
  f.close()
      
def write_article_to_file(article, index):
  full_text, metadata = split_article(article)
  write(full_text, "clean_data/full_text/" + str(index))
  write(metadata, "clean_data/metadata/" + str(index))

def find_articles(sections):
  regex = r'Document \d of \d'
  articles = []
  for section in sections:
    if re.match(regex, section[1]):
      articles.append(section)
  return articles

def find_sections(file_name):
  f = open(file_name)
  text = f.readlines()

  BREAK = "____________________________________________________________\r\n"

  current_section = []
  all_sections = []
  for line in text:
    if line != BREAK:
      current_section.append(line)
    elif line == BREAK:
      if len(current_section) > 0:
        all_sections.append(current_section)
        current_section = []
  all_sections.append(current_section)

  return all_sections

def write_file(file_name):
  sections = find_sections(file_name)
  articles = find_articles(sections)
  for i in range(0, len(articles)):
    write_article_to_file(articles[i], i)
    
if __name__ == '__main__':
  base_file_name = "ChrisJones-"
  #for i in range(0, 9):
  file_name = 'raw_data/ChrisJones-0.txt'
  write_file(file_name)
