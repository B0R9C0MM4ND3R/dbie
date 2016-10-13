import re

from dbie import clean_text


class TextProcessor:
    """This class contains methods to filter and analyze the formatted text form the analyzers."""

    def __init__(self, analyzer_type, url):
        """Initialize the variables needed for execution."""
        self.analyzer_type = analyzer_type
        self.pattern = re.compile(r'\d{4}')
        self.url = url

    def process(self, text):
        """This method takes the formatted text and performs the analysis"""
        filtered_text = self.__filter_text(text)
        simplified_data = self.__break_up_data(filtered_text)
        rotated_text = []
        for sent in simplified_data:
            rotated_text.append(self.__rotate_sent(sent))
        return self.__sort_list(rotated_text)

    def __filter_text(self, text):
        """This method filters the text, so only sentences with date and locations are left."""
        analyzer_num_tag = self.analyzer_type.num
        analyzer_noun_tag = self.analyzer_type.noun
        analyzer_loc_tag = self.analyzer_type.loc
        surname = clean_text.get_surname(self.url)
        sentence = []
        out_text = []
        surname_re = re.compile(r'' + surname)
        for sent in text:
            for token in sent:
                if (analyzer_num_tag in token and (self.pattern.match(token[0]) is not None)) or (
                                    analyzer_loc_tag in token and analyzer_noun_tag in token and surname_re.match(
                            str(token[0])) is None):
                    sentence.append(token)
            if [tup for tup in sentence if analyzer_num_tag in tup]:
                if [tup for tup in sentence if analyzer_loc_tag in tup]:
                    out_text.append(sentence)
            sentence = []
        return out_text

    def __break_up_data(self, data):
        """This method breaks up the sentences if they contain separate date and location mentions."""
        out = []
        out_sentence = []
        out_pretty = []
        out_pretty_sentence = []
        analyzer_num_tag = self.analyzer_type.num
        analyzer_noun_tag = self.analyzer_type.noun

        for sentence in data:
            num = False
            propn = False
            last = ""
            new_line = False
            for part in sentence:
                if num is False and propn is False and part[1] == analyzer_num_tag:
                    num = True
                elif num is False and propn is False and part[1] == analyzer_noun_tag:
                    propn = True
                elif num is False and propn and part[1] == analyzer_num_tag:
                    num = True
                    last = analyzer_num_tag
                elif num is False and propn and part[1] == analyzer_noun_tag:
                    last = analyzer_noun_tag
                elif num and propn is False and part[1] == analyzer_num_tag:
                    last = analyzer_num_tag
                elif num and propn is False and part[1] == analyzer_noun_tag:
                    propn = True
                    last = analyzer_noun_tag
                elif num and propn and last is analyzer_num_tag and part[1] == analyzer_noun_tag:
                    new_line = True
                elif num and propn and last is analyzer_noun_tag and part[1] == analyzer_num_tag:
                    new_line = True

                if not new_line:
                    out_sentence.append(part)
                else:
                    out.append(out_sentence)
                    out_sentence = [part]
                    num = False
                    propn = False
                    last = ""
                    new_line = False
            out.append(out_sentence)
            out_sentence = []
        # repairers falsely split sentences
        for sent in out:
            num = False
            loc = False
            for word in sent:
                if word[1] == analyzer_num_tag:
                    num = True
                else:
                    loc = True
                out_pretty_sentence.append(word[0])
            if num and loc:
                out_pretty.append(out_pretty_sentence)
                out_pretty_sentence = []
            else:
                out_pretty[-1] = out_pretty[-1] + out_pretty_sentence
                out_pretty_sentence = []

        return self.__prettify(out_pretty)

    @staticmethod
    def __prettify(text):
        """This method turns all elements of the text into strings."""
        pretty_text = []
        pretty_sentence = []
        for sentence in text:
            for token in sentence:
                pretty_sentence.append(str(token))
            pretty_text.append(pretty_sentence)
            pretty_sentence = []
        return pretty_text

    def __rotate_sent(self, sent):
        """This method rotates the sentences, so the date is in front of the location."""
        loc = []
        num = []
        for word in sent:
            if self.pattern.match(word):
                num.append(word)
            else:
                loc.append(word)
        seen = set()
        result = []
        for item in loc:
            if item not in seen:
                seen.add(item)
                result.append(item)
        loc = result
        num = sorted(num)
        return num + loc

    @staticmethod
    def __sort_list(unordered_list):
        """This method sorts the sentences by date."""
        ordered_list = sorted(unordered_list, key=lambda x: int(x[0][1:4]))
        return ordered_list
