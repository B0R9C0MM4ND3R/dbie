import re

from dbie import clean_text

from dbie.text_processor import TextProcessor


class AnalyzerSpacy:
    """This class uses the Spacy to analyze the text."""

    def __init__(self, analyzer_type):
        """Initialize the variables needed for execution."""
        self.text = []
        self.sentence = []
        self.date_pattern = re.compile(r'(\d{1,2}\.){2}\d{4}')
        self.url = ""
        self.analyzer_type = analyzer_type

    def analyze(self, url, spacy_nlp):
        """This method obtains the text and analyzes it."""
        # get text
        self.url = url
        text_processor = TextProcessor(self.analyzer_type, url)
        raw_text = clean_text.get_text(url)
        if raw_text is not None:
            # analyze the text
            splitted_text = spacy_nlp(raw_text)
            splitted_raw_text = []
            for sent in splitted_text.sents:
                splitted_raw_text.append(spacy_nlp(sent.text_with_ws))
            fixed_text = self.__fix_sent(splitted_raw_text)
            processed_text = text_processor.process(fixed_text)

            return processed_text
        else:
            print("Kein Lebenslauf vorhanden")
            return "Kein Lebenslauf vorhanden"

    @staticmethod
    def get_name(url):
        """This method returns the name of the current person, represented by the url."""
        return clean_text.get_title(url)

    def __fix_sent(self, text):
        """This method tries to fix simple sentence splitting mistakes and formats the text for further processing
        A word in a sentence is represented as: ('word','part-of-speech-tag','named-entity-tag')."""
        cleaned_text = []
        cleaned_sent = []
        for sent in text:
            # formatting the text
            for token in sent:
                word = token
                tag = token.pos_
                ner = token.ent_type_
                if 'NUM' in tag:
                    if self.date_pattern.match(word.text) is not None:
                        new_word = word.text[-4:]
                    else:
                        new_word = re.sub(r'\.', '', word.text)
                    element = (new_word, tag, ner)
                else:
                    element = (word, tag, ner)
                cleaned_sent.append(element)
            # fix sentence split
            if cleaned_text:
                last_sent = cleaned_text[-1]
                last_token = last_sent[-1]
                last_word = str(last_token[0])
                last_char = last_word[-1]
                if len(cleaned_sent) <= 3 and last_char is not '.':
                    for element in cleaned_sent:
                        cleaned_text[-1].append(element)
                else:
                    cleaned_text.append(cleaned_sent)
                cleaned_sent = []
            else:
                cleaned_text.append(cleaned_sent)
                cleaned_sent = []
        return cleaned_text
