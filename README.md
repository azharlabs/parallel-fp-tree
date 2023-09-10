# Parallel FP-Growth Implementation

This repository contains an implementation of the FP-growth algorithm for frequent itemset mining, enhanced to run in parallel using Python's multiprocessing module.

## Contents

1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [Usage](#usage)
4. [Functions Overview](#functions-overview)

## Introduction

FP-growth is a method used to discover frequent itemsets in a dataset. This implementation aims to optimize the mining process by parallelizing certain tasks, taking advantage of multi-core systems.

## Dependencies

- Python 3.x
- `multiprocessing`
- `concurrent.futures`
- External libraries (if any, add them here)

## Usage

To use this implementation:

1. Convert your transactions into a frequency dictionary using `convert_to_freq_dict(transactions)`.
2. Pass this dictionary and a minimum support threshold to `parallel_fp_growth(data, min_support)`.

Example:

```python
transactions = data_list = [['eggs', 'bacon', 'soup'],
             ['eggs', 'bacon', 'apple'],
             ['eggs', 'soup', 'bacon', 'banana']]
data = convert_to_freq_dict(transactions)
frequent_itemsets = parallel_fp_growth(data, 2)
print(frequent_itemsets)
```

## Functions Overview

- `TreeNode`: A class to represent a node in the FP-tree.
- `insert_tree`: Inserts a transaction into the FP-tree.
- `update_header`: Updates the header table with links to nodes.
- `find_conditional_pattern_base`: Finds the conditional pattern base for an item.
- `ascend_tree`: Traverses upwards from a node to the root in the FP-tree.
- `construct_fp_tree`: Constructs the main FP-tree.
- `parallel_mine`: Mines the FP-tree in parallel for a given item.
- `mine_tree`: Main function to mine the FP-tree.
- `convert_to_freq_dict`: Converts a list of transactions into a frequency dictionary.
- `create_and_mine_conditional_tree`: Creates and mines a conditional tree for an item.
- `parallel_fp_growth`: The main function to call to get the frequent itemsets.

---

## Contributing
We welcome contributions! Please fork the repository and submit a pull request with your improvements.

## Acknowledgments
Thanks to all the data miners out there for their continuous research and innovations.
Special shoutout to coffee for fueling this project. ☕

Happy data mining! 🚀📊🌳