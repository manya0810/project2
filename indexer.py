'''
@author: Sougata Saha
Institute: University at Buffalo
'''

from linkedlist import LinkedList
from collections import OrderedDict


class Indexer:
    def __init__(self):
        """ Add more attributes if needed"""
        self.inverted_index = OrderedDict({})

    def get_index(self):
        """ Function to get the index.
            Already implemented."""
        return self.inverted_index

    def generate_inverted_index(self, doc_id, tokenized_document):
        """ This function adds each tokenized document to the index. This in turn uses the function add_to_index
            Already implemented."""
        for t in tokenized_document:
            self.add_to_index(t, doc_id)

    def add_to_index(self, term_, doc_id_):
        """ This function adds each term & document id to the index.
            If a term is not present in the index, then add the term to the index & initialize a new postings list (linked list).
            If a term is present, then add the document to the appropriate position in the posstings list of the term.
            To be implemented."""
        if term_ not in self.inverted_index.keys():
            postings = LinkedList()
            postings.insert_at_end(doc_id_)
            self.inverted_index[term_] = postings
        else:
            postings = self.inverted_index[term_]
            postings.insert_at_end(doc_id_)

    def sort_terms(self):
        """ Sorting the index by terms.
            Already implemented."""
        sorted_index = OrderedDict({})
        for k in sorted(self.inverted_index.keys()):
            sorted_index[k] = self.inverted_index[k]
        self.inverted_index = sorted_index

    def add_skip_connections(self):
        """ For each postings list in the index, add skip pointers.
            To be implemented."""
        terms = self.inverted_index.keys()
        for term in terms:
            postings = self.inverted_index[term]
            postings.add_skip_connections()

    def calculate_tf_idf(self, doc_id_info):
        """ Calculate tf-idf score for each document in the postings lists of the index.
            To be implemented."""
        terms = self.inverted_index.keys()
        for term in terms:
            doc_frequency = 0
            term_frequencies = list()
            postings = self.inverted_index[term]
            doc_ids = postings.traverse_list()
            start_node = postings.start_node
            idf = len(doc_id_info.keys())/len(doc_ids)
            for doc_id in doc_ids:
                tokenized_text = doc_id_info[doc_id]
                term_frequency_in_doc = tokenized_text.count(term)
                doc_frequency = doc_frequency + term_frequency_in_doc
                tf = term_frequency_in_doc / len(tokenized_text)
                term_frequencies.append(tf)
                start_node.termFrequency = tf * idf
                start_node = start_node.next
