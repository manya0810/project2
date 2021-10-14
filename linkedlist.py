'''
@author: Sougata Saha
Institute: University at Buffalo
'''

import math


class Node:

    def __init__(self, value=None, next=None):
        """ Class to define the structure of each node in a linked list (postings list).
            Value: document id, Next: Pointer to the next node
            Add more parameters if needed.
            Hint: You may want to define skip pointers & appropriate score calculation here"""
        self.value = value
        self.next = next
        self.skipPointer = None
        self.termFrequency = None


class LinkedList:
    """ Class to define a linked list (postings list). Each element in the linked list is of the type 'Node'
        Each term in the inverted index has an associated linked list object.
        Feel free to add additional functions to this class."""

    def __init__(self):
        self.start_node = None
        self.end_node = None
        self.length, self.n_skips, self.idf = 0, 0, 0.0
        self.skip_length = None

    def traverse_list(self):
        traversal = []
        if self.start_node is None:
            return
        else:
            """ Write logic to traverse the linked list.
                To be implemented."""
            count = 0
            current_node = self.start_node
            while count < self.length:
                traversal.append(current_node.value)
                current_node = current_node.next
                count = count + 1
            return traversal

    def traverse_skips(self):
        traversal = []
        if self.start_node is None:
            return
        if self.start_node.skipPointer is not None:
            traversal.append(self.start_node.value)
            """ Write logic to traverse the linked list using skip pointers.
                To be implemented."""
            current_node = self.start_node
            while current_node != self.end_node:
                if current_node.skipPointer is None:
                    current_node = current_node.next
                else:
                    current_node = current_node.skipPointer
                    traversal.append(current_node.value)
            return traversal

    def add_skip_connections(self):
        n_skips = math.floor(math.sqrt(self.length))
        start = self.start_node
        if n_skips * n_skips == self.length:
            n_skips = n_skips - 1
        self.n_skips = n_skips
        self.skip_length = round(math.sqrt(self.length), 0)
        if self.length <= n_skips:
            return
        count = 0
        while count != self.n_skips:
            i = 0
            skip_pointing = start
            while i != self.skip_length:
                skip_pointing = skip_pointing.next
                i = i + 1
            start.skipPointer = skip_pointing
            start = skip_pointing
            count = count + 1
        """ Write logic to add skip pointers to the linked list. 
            This function does not return anything.
            To be implemented."""

    def insert_at_end(self, value):
        """ Write logic to add new elements to the linked list.
            Insert the element at an appropriate position, such that elements to the left are lower than the inserted
            element, and elements to the right are greater than the inserted element.
            To be implemented. """
        value_to_be_inserted = Node(value)
        if self.start_node is None:
            self.start_node = value_to_be_inserted
            self.end_node = value_to_be_inserted
            self.length = 1
            return
        if value in self.traverse_list():
            return
        elif self.start_node.value >= value:
            start_node_pointer = self.start_node
            self.start_node = value_to_be_inserted
            self.start_node.next = start_node_pointer
            self.length = self.length + 1
            return

        elif self.end_node.value <= value:
            self.end_node.next = value_to_be_inserted
            self.end_node = value_to_be_inserted
            self.length = self.length + 1
            return

        else:
            start_node_pointer = self.start_node
            while start_node_pointer.value < value < self.end_node.value and start_node_pointer.next is not None:
                start_node_pointer = start_node_pointer.next
            m = self.start_node
            while m.next != start_node_pointer and m.next is not None:
                m = m.next
            m.next = value_to_be_inserted
            value_to_be_inserted.next = start_node_pointer
            self.length = self.length + 1
            return
