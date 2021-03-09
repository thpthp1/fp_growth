from types import SimpleNamespace
from collections import namedtuple
from itertools import chain, combinations
from pprint import pprint


class Node:
    def __init__(self, name, frequency, parent):
        self.name = name
        self.freq = frequency
        self.parent = parent
        self.children = {}
        self.next = None

    def increment(self, frequency):
        self.freq += frequency
        

def read_data(filename, sep=','):
    transactions = []
    freqs = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.rstrip()
            if not line: continue
            line = line.split(sep)
            transactions.append(line)
            for item in line:
                freqs[item] = freqs.get(item, 0) + 1
    return transactions, freqs

def fp_tree(transations, freqs: dict, min_sup=0.4):
    total = len(transations)
    table = {item: SimpleNamespace(freq=freq, node=None) 
                for item, freq in freqs.items() if freq/total >= min_sup}

    if(len(table) == 0):
        return None, None
    #print(filter_l1)
    fp_tree = Node('{}', 1, None)

    # Generate the tree with connection to the table
    for trans in transations:
        trans = list(filter(lambda x: x in table, trans))
        # Sorted in desceding order
        trans.sort(key=lambda item: table[item].freq, reverse=True)
        # print(trans)
        curr = fp_tree
        for item in trans:
            # Update from the current root
            if item in curr.children:
                curr.children[item].increment(1)
            else:
                _add_table_pointer(table, curr, item)
            curr = curr.children[item]
    return fp_tree, table

def freq_item_sets(table, prevs: set, freq_sets, min_sup=0.4):
    sorted_table = dict(sorted(table.items(), key=lambda item: item[1].freq))
    for item in sorted_table:
        freq_items = prevs.copy()
        freq_items.add(item)
        freq_sets.append(freq_items)
        conditional_trans, freqs = conditionals(item, table)
        cond_tree, cond_table = fp_tree(conditional_trans, freqs) 
        if cond_table:
            freq_item_sets(cond_table, freq_items, freq_sets)

def _ascend_tree(node, prevs):
    if node.parent:
        prevs.append(node.name)
        _ascend_tree(node.parent, prevs)

def conditionals(item, table):
    node = table[item].node 
    transaction = []
    freqs = {}
    while node != None:
        prev_paths = []
        _ascend_tree(node, prev_paths)  
        if len(prev_paths) > 1:
            transaction.append(prev_paths[1:])
            freqs[node.name] = node.freq
        node = node.next  
    for trans in transaction:
        for item in trans:
            freqs[item] = freqs.get(item, 0) + 1 
    return transaction, freqs

def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

def support(itemset, transaction):
    count = 0
    for trans in transaction:
        if(set(itemset).issubset(trans)):
            count += 1
    return count


def association_rules(transactions, freqs: dict, freq_sets: set, min_conf=0.6):
    Rule = namedtuple("Rule", ['A', 'B', 'conf'])
    rules = []
    for item_set in freq_sets:
        subsets = powerset(item_set)
        sup = support(item_set, transactions)
        for ss in subsets:
            conf = float(sup / support(ss, transactions))
            if conf >= min_conf:
                rules.append(Rule(ss, set(item_set.difference(ss)), conf))
    return rules
    

def _add_table_pointer(table, curr, item):
    new_node = Node(item, 1, curr)
    curr.children[item] = new_node
    # link from table
    if table[item].node:
        curr_node = table[item].node
        while curr_node.next:
            curr_node = curr_node.next
        curr_node.next = new_node
    else:
        table[item].node = new_node

if __name__ == '__main__':
    trans, freqs = read_data('table.csv')
    tree, table = fp_tree(trans, freqs)
    freq_sets = []
    freq_item_sets(table, set(), freq_sets)
    pprint(freq_sets)
    pprint(association_rules(trans, freqs, freq_sets))
