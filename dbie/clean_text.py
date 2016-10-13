from bs4 import BeautifulSoup
import re
import urllib.request

"""This file contains functions to get text from the website and clean it for the analyzer."""

# regex pattern to differentiate between the two databases.
pattern_ndb = re.compile(r'ndbcontent')


def get_soup(url):
    """This function fetches the content of the website"""
    response = urllib.request.urlopen(url)
    data = response.read()
    return BeautifulSoup(data, 'html.parser')


def get_title(url):
    """This function returns the name of the person on the website"""
    soup = get_soup(url)
    full_name = re.sub('Deutsche Biographie -  ', '', soup.html.head.title.get_text()) + "\n"
    output = ""
    full_name = re.sub('\((.)*?\)', '', full_name)
    if ',' in full_name:
        splitted_name = [x.split() for x in full_name.split(',')]
        for name in splitted_name[1]:
            output = output + name + " "
        for surname in splitted_name[0]:
            output = output + surname + " "
        return output
    else:
        return full_name


def __get_name_abr(url):
    """This function returns the first letter of the persons name on the website"""
    soup = get_soup(url)
    name = re.sub('Deutsche Biographie -  ', '', soup.html.head.title.get_text()) + "\n"
    splitted_name = [x.split() for x in name.split(',')]
    return splitted_name[0][0][0]


def __get_bio(url):
    """"This function extracts the needed text from the websites content"""
    soup = get_soup(url)
    if pattern_ndb.match(url[-10:]) is not None:
        bio_id = "ndbcontent_leben"
    else:
        bio_id = "adbcontent_leben"
    for li in soup.findAll("li", {"class": "artikel"}):
        for h4 in li.findAll("h4", {"id": bio_id}):
            if h4 is not None:
                text = li.prettify()
                myregex = r'' + re.escape(__get_name_abr(url)) + '\.'
                namereplacedtext = re.sub(myregex, get_title(url), text)
                return __cleanup(re.sub('<(.|\n)*?>', ' ', namereplacedtext))


def __cleanup(text):
    """This function performs basic cleanup of the text"""
    pattern = re.compile(r'\d{4}-\d{2}\b')
    text = re.sub('—', '-', text)
    text = re.sub('–', '-', text)
    matches = pattern.findall(text)
    if matches is not None:
        for element in matches:
            text = re.sub(element, element[:5]+element[:2]+element[5:], text)
    text = re.sub('†', 'gestorben', text)
    text = re.sub('geb.', 'geboren', text)
    text = re.sub('→', ' ', text)
    text = re.sub('&amp;', 'und', text)
    text = text[6:]
    text = re.sub('\s+', ' ', text).strip()
    return text


def get_text(url):
    """This function returns the clean text"""
    return __get_bio(url)


def get_surname(url):
    """This function returns the surname of the person on the website"""
    soup = get_soup(url)
    full_name = re.sub('Deutsche Biographie -  ', '', soup.html.head.title.get_text()) + "\n"
    surname_out = ""
    full_name = re.sub('\((.)*?\)', '', full_name)
    if ',' in full_name:
        splitted_name = [x.split() for x in full_name.split(',')]
        for surname in splitted_name[0]:
            surname_out = surname
    else:
        surname_out = full_name
    return surname_out
