from bs4 import BeautifulSoup
import urllib
from string import ascii_lowercase

class Line:
  def __init__(self, line):
    self.data = unicode((line.contents[0]))
    self.href = line.attrs['href']
    self.data_type = self.decide_data_type()

  def decide_data_type(self):
    if "personId" in self.href:
      return "person"
    elif "theaterId" in self.href:
      return "theater"
    else:
      return None

class Scraper:
  BASE_URL = "http://www.chicagotheatrehistoryproject.org/database.php?letter="

  def build_request(self, letter):
    return self.BASE_URL + letter

  def make_soup(self, request):
    r = urllib.urlopen(request).read()
    return BeautifulSoup(r)

  def find_and_write_data(self, soup):
    people_file = open('people.txt', 'a')
    theatre_file = open('theaters.txt', 'a')
    lines = soup.find_all('a') 
    for line in lines:
      l = Line(line)
      if l.data_type == "person":
        people_file.write(l.data + "\n")
      elif l.data_type == "theater":
        theatre_file.write(l.data + "\n")

    people_file.close()
    theatre_file.close()

  def do_all_the_things(self):
    for letter in ascii_lowercase:
      url = self.build_request(letter)
      soup = self.make_soup(url)
      self.find_and_write_data(soup)
   
s = Scraper()
s.do_all_the_things()

