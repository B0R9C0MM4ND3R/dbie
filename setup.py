#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='Deutsche Biographie - Information Extractor',
    version='1.0',
    author='Christop Stemp und Andreas Vogt',
    description='Extrahiert Ort und Zeitangaben über eine Person der Deutschen Biographie',
    install_requires=['pillow', 'pycorenlp', 'spacy', 'beautifulsoup4']
    )
