import urllib.request
import urllib.error
import socket


# checks if a connection to the given url can be established
def check_url(url):
    try:
        urllib.request.urlopen(url, timeout=1)
        return True
    except urllib.error.URLError:
        return False
    except socket.error:
        return False
