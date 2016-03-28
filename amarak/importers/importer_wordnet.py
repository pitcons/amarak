# encoding: utf8
import nltk
from nltk.corpus import wordnet as wn

def import_wordnet():
    for synset in wn.synsets('food'):
        for lemma in synset.lemmas():
            print lemma.name()


if __name__ == '__main__':
    import_wordnet()
