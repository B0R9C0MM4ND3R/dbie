class Analyzer(object):
    """Analyzer datatype, containing the name of the tagger, the number, location and proper noun tag"""
    def __init__(self, name, num, loc, noun):
        self.name = name
        self.num = num
        self.loc = loc
        self.noun = noun
