from dbie import clean_text
from dbie.text_processor import TextProcessor


class AnalyzerStanford:
    """This class uses the Stanford coreNLP to analyze the text."""

    def __init__(self, analyzer_type):
        """Initialize the variables needed for execution."""
        self.analyzer_type = analyzer_type

    def analyze(self, url, nlp_server):
        """This method obtains the text and analyzes it."""
        # get text
        text_processor = TextProcessor(self.analyzer_type, url)
        text = clean_text.get_text(url)
        if text is not None:
            # analyze the text
            output = nlp_server.annotate(text, properties={
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
            fixed_text = self.__fix_sent(output)
            processed_text = text_processor.process(fixed_text)

            return processed_text
        else:
            print("Kein Lebenslauf vorhanden")
            return "Kein Lebenslauf vorhanden"

    @staticmethod
    def get_name(url):
        """This method returns the name of the current person, represented by the url."""
        return clean_text.get_title(url)

    @staticmethod
    def __fix_sent(text):
        """This method takes the text and formats it for further processing.
        A word in a sentence is represented as: ('word','part-of-speech-tag','named-entity-tag')."""
        word = ""
        pos = ""
        ner = ""
        out_sent = []
        out_text = []
        for y in range(0, len(text['sentences']) - 1):
            for x in text['sentences'][y]['tokens']:
                for k, v in x.items():
                    if k == "word":
                        word = v
                    if k == "pos":
                        pos = v
                    if k == 'ner':
                        ner = v
                element = (word, pos, ner)
                out_sent.append(element)
            out_text.append(out_sent)
            out_sent = []
        return out_text
