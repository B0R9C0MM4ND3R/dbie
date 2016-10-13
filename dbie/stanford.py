import os
import threading
from subprocess import Popen
from tempfile import gettempdir
import shlex
import urllib.request
import urllib.error


class Server(threading.Thread):
    command = """java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -props StanfordCoreNLP-german.properties"""
    file_path = os.path.dirname(__file__) + os.path.sep + "corenlp"

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        os.chdir(self.file_path)
        print(os.getcwd())
        Popen(shlex.split(self.command))


# stops the background server
def stop():
    path = gettempdir() + os.path.sep + "corenlp.shutdown"
    f = open(path, "r")
    key = f.read()
    key.replace("\n", "")
    server_url = "http://localhost:9000/shutdown?key="
    urllib.request.urlopen(server_url + key, timeout=1)
    f.close()


# loads the classifiers into the server
def preload_classifiers(nlp):
    nlp.annotate("", properties={
        'annotators': 'ner, pos',
        'tokenize.language': 'de',
        'pos.model': 'edu/stanford/nlp/models/pos-tagger/german/german-dewac.tagger',
        'ner.model': 'edu/stanford/nlp/models/ner/german.dewac_175m_600.crf.ser.gz',
        'ner.applyNumericClassifiers': 'false',
        'ner.useSUTime': 'false',
        'parse.model': 'edu/stanford/nlp/models/srparser/germanSR.ser.gz',
        'outputFormat': 'json',
        'encoding': 'UTF-8'
    })
