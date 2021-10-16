'''
@author: Sougata Saha
Institute: University at Buffalo
'''

from tqdm import tqdm
from preprocessor import Preprocessor
from indexer import Indexer
from collections import OrderedDict
from linkedlist import LinkedList
from linkedlist import Node
import inspect as inspector
import sys
import argparse
import json
import time
import random
import flask
from flask import Flask
from flask import request
import hashlib

app = Flask(__name__)


class ProjectRunner:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.indexer = Indexer()
        self.docIdInfo = OrderedDict({})

    def _sort_list_acc_to_tf_idf(self, list):
        list_pointer = list.start_node
        tf_idf_sorted_value = LinkedList()
        while list_pointer is not None:
            node_to_be_inserted = Node()
            node_to_be_inserted.value = list_pointer.value
            node_to_be_inserted.termFrequency = list_pointer.termFrequency
            if tf_idf_sorted_value.start_node is None:
                tf_idf_sorted_value.start_node = node_to_be_inserted
                tf_idf_sorted_value.end_node = node_to_be_inserted
                tf_idf_sorted_value.length = 1
            elif tf_idf_sorted_value.start_node.termFrequency >= list_pointer.termFrequency:
                start_node_pointer = tf_idf_sorted_value.start_node
                tf_idf_sorted_value.start_node = node_to_be_inserted
                tf_idf_sorted_value.start_node.next = start_node_pointer
                tf_idf_sorted_value.length = tf_idf_sorted_value.length + 1

            elif tf_idf_sorted_value.end_node.termFrequency <= list_pointer.termFrequency:
                tf_idf_sorted_value.end_node.next = node_to_be_inserted
                tf_idf_sorted_value.end_node = node_to_be_inserted
                tf_idf_sorted_value.length = tf_idf_sorted_value.length + 1

            else:
                tf_idf_sorted_value_start_node_pointer = tf_idf_sorted_value.start_node
                while tf_idf_sorted_value_start_node_pointer.termFrequency < list_pointer.termFrequency < tf_idf_sorted_value.end_node.termFrequency:
                    tf_idf_sorted_value_start_node_pointer = tf_idf_sorted_value_start_node_pointer.next
                m = tf_idf_sorted_value.start_node
                while m.next != tf_idf_sorted_value_start_node_pointer and m.next is not None:
                    m = m.next
                m.next = node_to_be_inserted
                node_to_be_inserted.next = tf_idf_sorted_value_start_node_pointer
                tf_idf_sorted_value.length = tf_idf_sorted_value.length + 1
            list_pointer = list_pointer.next
        return tf_idf_sorted_value.traverse_list()[::-1]

    def _merge_without_skip(self, list1, list2):
        comparisons = 0
        common_list = LinkedList()
        start_list1 = list1.start_node
        start_list2 = list2.start_node
        while start_list1 is not None and start_list2 is not None:
            if start_list1.value == start_list2.value:
                common_list.insert_at_end(start_list1.value)
                start_common = common_list.start_node
                while start_list1.value != start_common.value:
                    start_common = start_common.next
                start_common.termFrequency = max(start_list1.termFrequency, start_list2.termFrequency)
                start_list1 = start_list1.next
                start_list2 = start_list2.next
                comparisons = comparisons + 1
            elif start_list1.value > start_list2.value:
                start_list2 = start_list2.next
                comparisons = comparisons + 1
            elif start_list1.value < start_list2.value:
                start_list1 = start_list1.next
                comparisons = comparisons + 1
        return comparisons, common_list

    def _merge_with_skip(self, list1, list2):
        comparisons = 0
        common_list = LinkedList()
        start_list1 = list1.start_node
        start_list2 = list2.start_node
        while start_list1 is not None and start_list2 is not None:
            if start_list1.value == start_list2.value:
                common_list.insert_at_end(start_list1.value)
                start_common = common_list.start_node
                while start_list1.value != start_common.value:
                    start_common = start_common.next
                start_common.termFrequency = max(start_list1.termFrequency, start_list2.termFrequency)
                start_list1 = start_list1.next
                start_list2 = start_list2.next
                comparisons = comparisons + 1
            elif start_list1.value < start_list2.value:
                comparisons = comparisons + 1
                if (start_list1.skipPointer is not None) and (start_list1.skipPointer.value <= start_list2.value):
                    while (start_list1.skipPointer is not None) and (
                            start_list1.skipPointer.value <= start_list2.value):
                        start_list1 = start_list1.skipPointer
                else:
                    start_list1 = start_list1.next
            elif (start_list2.skipPointer is not None) and (start_list2.skipPointer.value <= start_list1.value):
                comparisons = comparisons + 1
                while (start_list2.skipPointer is not None) and (start_list2.skipPointer.value <= start_list1.value):
                    start_list2 = start_list2.skipPointer
            else:
                start_list2 = start_list2.next
                comparisons = comparisons + 1

        return comparisons, common_list

    def _daat_and(self, input_arr_query, index):
        """ Implement the DAAT AND algorithm, which merges the postings list of N query terms.
            Use appropriate parameters & return types.
            To be implemented."""
        list1 = None
        list2 = None
        final_list = None
        comparison = 0
        total_comparison = 0
        for term in input_arr_query:
            if list1 is None:
                list1 = index[term]
            elif list2 is None:
                list2 = index[term]
            if list1 is not None and list2 is not None:
                comparison, final_list = self._merge_without_skip(list1, list2)
                list1 = final_list
                list2 = None
            total_comparison = total_comparison + comparison

        final_list_without_skip = final_list.traverse_list()
        total_comparison_without_skip = total_comparison
        final_list_without_skip_tf_idf = self._sort_list_acc_to_tf_idf(final_list)

        final_list = None
        total_comparison = 0
        comparison = 0
        list1 = None
        list2 = None
        new_index = self._sort_acc_to_postingsList_length(index, input_arr_query)
        for term in input_arr_query:
            if final_list is not None:
                list1.add_skip_connections()
            if list1 is None:
                list1 = new_index[term]
            elif list2 is None:
                list2 = new_index[term]
            if list1 is not None and list2 is not None:
                comparison, final_list = self._merge_with_skip(list1, list2)
                list1 = final_list
                list2 = None
            total_comparison = total_comparison + comparison
        final_list_with_skip = final_list.traverse_list()
        total_comparison_with_skip = total_comparison
        fina_list_with_skip_tf_idf = self._sort_list_acc_to_tf_idf(final_list)
        return final_list_without_skip, total_comparison_without_skip, final_list_with_skip, total_comparison_with_skip, final_list_without_skip_tf_idf, total_comparison_without_skip, fina_list_with_skip_tf_idf, total_comparison_with_skip

    def _sort_acc_to_postingsList_length(self, index, queries):
        length = []
        for term in queries:
           length.append(index[term])
        length.sort()
        new_index = OrderedDict()
        terms = []
        for i in range(0, len(length)):
            for term in queries:
                if index[term].length == length[i] and term not in terms:
                    new_index[term] = index[term]
                    terms.append(term)
        return new_index

    def _get_postings(self, index, term):
        """ Function to get the postings list of a term from the index.
            Use appropriate parameters & return types.
            To be implemented."""
        return index[term].traverse_list(), index[term].traverse_skips()

    def _output_formatter(self, op):
        """ This formats the result in the required format.
            Do NOT change."""
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def run_indexer(self, corpus):
        """ This function reads & indexes the corpus. After creating the inverted index,
            it sorts the index by the terms, add skip pointers, and calculates the tf-idf scores.
            Already implemented, but you can modify the orchestration, as you seem fit."""
        with open(corpus, 'r', encoding="utf-8") as fp:
            for line in tqdm(fp.readlines()):
                doc_id, document = self.preprocessor.get_doc_id(line)
                tokenized_document = self.preprocessor.tokenizer(document)
                self.docIdInfo[doc_id] = tokenized_document
                self.indexer.generate_inverted_index(doc_id, tokenized_document)
        self.indexer.sort_terms()
        self.indexer.add_skip_connections()
        self.indexer.calculate_tf_idf(self.docIdInfo)

    def sanity_checker(self, command):
        """ DO NOT MODIFY THIS. THIS IS USED BY THE GRADER. """

        index = self.indexer.get_index()
        kw = random.choice(list(index.keys()))
        return {"index_type": str(type(index)),
                "indexer_type": str(type(self.indexer)),
                "post_mem": str(index[kw]),
                "post_type": str(type(index[kw])),
                "node_mem": str(index[kw].start_node),
                "node_type": str(type(index[kw].start_node)),
                "node_value": str(index[kw].start_node.value),
                "command_result": eval(command) if "." in command else ""}

    def run_queries(self, query_list, random_command):
        """ DO NOT CHANGE THE output_dict definition"""
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       'sanity': self.sanity_checker(random_command)
                       }

        index = self.indexer.get_index()
        for query in tqdm(query_list):
            """ Run each query against the index. You should do the following for each query:
                1. Pre-process & tokenize the query.
                2. For each query token, get the postings list & postings list with skip pointers.
                3. Get the DAAT AND query results & number of comparisons with & without skip pointers.
                4. Get the DAAT AND query results & number of comparisons with & without skip pointers, 
                    along with sorting by tf-idf scores."""
            input_term_arr = self.preprocessor.tokenizer(query)

            for term in input_term_arr:
                postings, skip_postings = self._get_postings(index, term)
                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""

                output_dict['postingsList'][term] = postings
                output_dict['postingsListSkip'][term] = skip_postings

            for term in input_term_arr:
                postings, skip_postings = self._get_postings(index, term)
                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""

                output_dict['postingsList'][term] = postings
                output_dict['postingsListSkip'][term] = skip_postings
            """ Implement logic to populate initialize the above variables.
                The below code formats your result to the required format.
                To be implemented."""
            and_op_no_skip, and_comparisons_no_skip, and_op_skip, and_comparisons_skip, and_op_no_skip_sorted, and_comparisons_no_skip_sorted, and_op_skip_sorted, and_comparisons_skip_sorted = \
                self._daat_and(input_term_arr, index)
            and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip)
            and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
            and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(
                and_op_no_skip_sorted)
            and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)

            output_dict['daatAnd'][query.strip()] = {}
            output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
            output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
            output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

            output_dict['daatAndSkip'][query.strip()] = {}
            output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
            output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
            output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

            output_dict['daatAndTfIdf'][query.strip()] = {}
            output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

            output_dict['daatAndSkipTfIdf'][query.strip()] = {}
            output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted

        return output_dict


@app.route("/execute_query", methods=['POST'])
def execute_query():
    """ This function handles the POST request to your endpoint.
        Do NOT change it."""
    start_time = time.time()

    queries = request.json["queries"]
    random_command = request.json["random_command"]

    """ Running the queries against the pre-loaded index. """
    output_dict = runner.run_queries(queries, random_command)

    """ Dumping the results to a JSON file. """
    with open("D:\IR\project2\data\output.json", 'w') as fp:
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time),
        "username_hash": username_hash
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    """ Driver code for the project, which defines the global variables.
        Do NOT change it."""

    output_location = "project2_output.json"
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)
    parser.add_argument("--username", type=str,
                        help="Your UB username. It's the part of your UB email id before the @buffalo.edu. "
                             "DO NOT pass incorrect value here")

    argv = parser.parse_args()

    corpus = argv.corpus
    output_location = argv.output_location
    username_hash = hashlib.md5(argv.username.encode()).hexdigest()

    """ Initialize the project runner"""
    runner = ProjectRunner()

    """ Index the documents from beforehand. When the API endpoint is hit, queries are run against 
        this pre-loaded in memory index. """
    runner.run_indexer(corpus)

    app.run(host="0.0.0.0", port=9999)
