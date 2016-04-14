# -*- coding: utf-8 -*-
import os
import requests

from concept import *
from concept_scheme import *
from link import *
from relation import *
from label import Label
from exception import *

# class AmarakClient(object):

#     def __init__(self, base_url):
#         self.base_url = base_url
#         self.thesarurus_name = None

#     def select(self, thesarurus_name):
#         self.thesarurus_name = thesarurus_name

#     def thesauruses(self):
#         url = os.path.join(self.base_url, 'thesauruses')
#         response = requests.get(url)
#         result = response.json()
#         return result

#     def schemes(self):
#         url = os.path.join(self.base_url, 'schemes')
#         response = requests.get(url)
#         result = response.json()
#         return result

#     def term_by_word(self, word):
#         url = os.path.join(self.base_url, self.thesarurus_name, 'fetch_terms')
#         response = requests.get(url, {'word': word})
#         result = response.json()
#         return result
