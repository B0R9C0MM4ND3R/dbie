from dbie import clean_text

# this is a help class to get the data from adb and ndb

url = "https://www.deutsche-biographie.de"
alpha_url = url + "/alpha"


# returns the letter and the belonging url from ndb
def get_all_ndb():
    return __get_all_general("/name/ndb/")


# returns the letter and the belonging url from adb
def get_all_adb():
    return __get_all_general("/name/adb/")


# returns the letter and the belonging url
def __get_all_general(part_url):
    soup = clean_text.get_soup(alpha_url)
    array = []
    for ul in soup.findAll("ul", {"class": "list-inline"}):
        for li in ul.findAll("li"):
            for a in li.findAll("a"):
                element = a.__str__()
                if part_url in element:
                    tuple = (a.get_text(), a.get("href"))
                    array.append(tuple)
    return array


# returns all letters from adb
def get_all_adb_letters():
    letter = []
    for (x, y) in get_all_adb():
        letter.append(x)
    return letter


# returns all available names with the given url
def get_all_ndb_adb_names(url_letter):
    soup = clean_text.get_soup(url + url_letter)
    if "ndb" in url_letter:
        part_url = "#ndbcontent"
    else:
        part_url = "#adbcontent"
    array = []
    for div in soup.findAll("div", {"class": "panel-body"}):
        for ul in div.findAll("ul"):
            for li in ul.findAll("li"):
                for a in li.findAll("a"):
                    element = a.__str__()
                    if part_url in element:
                        tuple = (a.get_text(), a.get("href"))
                        array.append(tuple)
    return array


# returns all letters from ndb
def get_all_ndb_letters():
    letter = []
    for (x, y) in get_all_ndb():
        letter.append(x)
    return letter
