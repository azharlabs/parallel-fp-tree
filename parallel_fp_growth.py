import multiprocessing
import concurrent.futures
from multiprocessing import Pool, Manager, cpu_count

class TreeNode:
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None

def insert_tree(transaction, tree, header_table, count):
    if transaction[0] in tree.children:
        tree.children[transaction[0]].count += count
    else:
        tree.children[transaction[0]] = TreeNode(transaction[0], count, tree)
        if header_table[transaction[0]][1] is None:
            header_table[transaction[0]][1] = tree.children[transaction[0]]
        else:
            update_header(header_table[transaction[0]][1], tree.children[transaction[0]])
    if len(transaction) > 1:
        insert_tree(transaction[1:], tree.children[transaction[0]], header_table, count)

def update_header(node, target_node):
    while node.link is not None:
        node = node.link
    node.link = target_node

def find_conditional_pattern_base(node):
    patterns = []
    while node is not None:
        prefix_path = ascend_tree(node)
        if len(prefix_path) > 1:
            patterns.append((tuple(prefix_path[1:]), node.count))
        node = node.link
    return patterns

def ascend_tree(node):
    path = []
    while node and node.parent:
        path.append(node.item)
        node = node.parent
    return path


def construct_fp_tree(data, min_support):
    item_counts = {}
    for transaction, count in data.items():
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + count

    item_counts = {k: v for k, v in item_counts.items() if v >= min_support}
    header_table = {item: [count, None] for item, count in item_counts.items()}
    tree_root = TreeNode(None, 1, None)

    for transaction, count in data.items():
        sorted_items = [item for item in transaction if item in item_counts]
        sorted_items.sort(key=lambda x: item_counts[x], reverse=True)
        if len(sorted_items) > 0:
            insert_tree(sorted_items, tree_root, header_table, count)
    return tree_root, header_table

def parallel_mine(item, header_table, min_support, prefix):
    # Extract only necessary data from the header table
    count, node = header_table[item]
    frequent_itemsets = {}
    new_prefix = prefix.copy()
    new_prefix.add(item)
    frequent_itemsets[tuple(sorted(new_prefix))] = header_table[item][0]

    conditional_pattern_base = find_conditional_pattern_base(header_table[item][1])
    conditional_tree_data = {}
    for pattern, count in conditional_pattern_base:
        conditional_tree_data[pattern] = count

    conditional_tree_root, conditional_header_table = construct_fp_tree(conditional_tree_data, min_support)
    if conditional_header_table:
        mine_tree(conditional_header_table, min_support, new_prefix, frequent_itemsets, is_parallel=False)
    return frequent_itemsets

def mine_tree(header_table, min_support, prefix, frequent_itemsets, is_parallel=True):
    sorted_items = sorted(list(header_table.keys()), key=lambda p: header_table[p][0])
    
    if is_parallel:  
        with Pool(int(cpu_count() / 2)) as pool:
            # Pass only necessary data
            results = pool.starmap(parallel_mine, [(item, {item: header_table[item]}, min_support, prefix) for item in sorted_items])
            
        for result in results:
            frequent_itemsets.update(result)
    else:
        for item in sorted_items:
            local_frequent_itemsets = parallel_mine(item, {item: header_table[item]}, min_support, prefix)
            frequent_itemsets.update(local_frequent_itemsets)



def convert_to_freq_dict(transactions):
    freq_dict = {}
    for transaction in transactions:
        transaction_tuple = tuple(sorted(transaction))
        freq_dict[transaction_tuple] = freq_dict.get(transaction_tuple, 0) + 1
    return freq_dict





def create_and_mine_conditional_tree(item, header_table, min_support, prefix):
    # Construct conditional pattern base for the current item
    conditional_pattern_base = find_conditional_pattern_base(header_table[item][1])
    conditional_tree_data = {}
    for pattern, count in conditional_pattern_base:
        conditional_tree_data[pattern] = count
    
    # Build a conditional FP-tree for the item
    conditional_tree_root, conditional_header_table = construct_fp_tree(conditional_tree_data, min_support)
    
    # Mine the conditional FP-Tree
    frequent_itemsets = {}
    if conditional_header_table:
        mine_tree(conditional_header_table, min_support, prefix, frequent_itemsets, is_parallel=False)
    return frequent_itemsets

def parallel_fp_growth(data, min_support):
    tree, header_table = construct_fp_tree(data, min_support)
    sorted_items = sorted(list(header_table.keys()), key=lambda p: header_table[p][0])
    print("cpu count===============>", cpu_count())
    
    # Use ThreadPoolExecutor to process each item in parallel
    frequent_itemsets = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(cpu_count() / 2)) as executor:
        futures = {executor.submit(create_and_mine_conditional_tree, item, header_table, min_support, set([item])): item for item in sorted_items}
        
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                data = future.result()
                for key, value in data.items():
                    frequent_itemsets[key] = frequent_itemsets.get(key, 0) + value
            except Exception as exc:
                print(f'Item {item} generated an exception: {exc}')

    return frequent_itemsets
