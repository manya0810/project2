'''
@author: Sougata Saha
Institute: University at Buffalo
'''

import collections
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')


class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()

    def get_doc_id(self, doc):
        """ Splits each line of the document, into doc_id & text.
            Already implemented"""
        arr = doc.split("\t")
        return int(arr[0]), arr[1]

    def tokenizer(self, text):
        """ Implement logic to pre-process & tokenize document text.
            Write the code in such a way that it can be re-used for processing the user's query.
            To be implemented."""
        text = text.lower()
        text = re.sub('[^a-zA-Z0-9 ]', ' ', text)
        text.strip()
        text = " ".join(text.split())
        token_after_whitespace_tokens = text.split()
        token_after_stopwords_removal = list()
        for token in token_after_whitespace_tokens:
            if token not in self.stop_words:
                token_after_stopwords_removal.append(token)
        token_after_stemming = [self.ps.stem(word) for word in token_after_stopwords_removal]
        return token_after_stemming
