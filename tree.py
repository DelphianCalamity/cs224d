import random
# This file contains the dataset in a useful way. We populate a list of
# Trees to train/test our Neural Nets such that each Tree contains any
# number of Node objects.

# The best way to get a feel for how these objects are used in the program is to drop pdb.set_trace() in a few places throughout the codebase
# to see how the trees are used.. look where loadtrees() is called etc..


class Node:  # a node in the tree
    def __init__(self, label, word=None):
        self.label = label
        self.word = word
        self.parent = None  # reference to parent
        self.left = None  # reference to left child
        self.right = None  # reference to right child
        # true if I am a leaf (could have probably derived this from if I have
        # a word)
        self.isLeaf = False
        # true if we have finished performing fowardprop on this node (note,
        # there are many ways to implement the recursion.. some might not
        # require this flag)

    def __str__(self):
        if self.isLeaf:
            return '[{0}:{1}]'.format(self.word, self.label)
        return '({0} <- [{1}:{2}] -> {3})'.format(self.left, self.word, self.label, self.right)


class Tree:

    def __init__(self, treeString, openChar='(', closeChar=')'):
        tokens = []
        self.open = '('
        self.close = ')'
        self.max_depth = 0
        self.num_nodes = 0
        for toks in treeString.strip().split():
            tokens += list(toks)
        self.root = self.parse(tokens)
        # get list of labels as obtained through a post-order traversal
        self.labels = get_labels(self.root)
        # print(self.labels)
        self.num_words = len(self.labels)


    def parse(self, tokens, parent=None, i=0):
        assert tokens[0] == self.open, "Malformed tree"
        assert tokens[-1] == self.close, "Malformed tree"

        split = 2  # position after open and label
        countOpen = countClose = 0

        if tokens[split] == self.open:
            countOpen += 1
            split += 1
        # Find where left child and right child split
        while countOpen != countClose:
            if tokens[split] == self.open:
                countOpen += 1
            if tokens[split] == self.close:
                countClose += 1
            split += 1

        # New node
        node = Node(int(tokens[1]))  # zero index labels
        self.num_nodes += 1
        node.parent = parent

        # leaf Node
        if countOpen == 0:
            node.word = ''.join(tokens[2:-1]).lower()  # lower case?
            node.isLeaf = True
            if i > self.max_depth:
                self.max_depth = i
            return node

        node.left = self.parse(tokens[2:split], parent=node, i=i+1)
        node.right = self.parse(tokens[split:-1], parent=node, i=i+1)

        return node

    def get_words(self):
        leaves = getLeaves(self.root)
        words = [node.word for node in leaves]
        return words

def get_max_tree_height(data):
    max_height = 0
    for tree in data:
        if tree.max_depth > max_height:
            max_height = tree.max_depth
    return max_height

def get_max_tree_nodes(data):
    max_nodes = 0
    for tree in data:
        if tree.num_nodes > max_nodes:
            max_nodes = tree.num_nodes
    return max_nodes

def leftTraverse(node, nodeFn=None, args=None):
    """
    Recursive function traverses tree
    from left to right.
    Calls nodeFn at each node
    """
    if node is None:
        return
    leftTraverse(node.left, nodeFn, args)
    leftTraverse(node.right, nodeFn, args)
    nodeFn(node, args)

def traverse(node, nodeFn=None, args=None):
    if node is None:
        return

    nodeFn(node, args)
    traverse(node.left, nodeFn, (args[0], args[1]*2))
    traverse(node.right, nodeFn, (args[0], args[1]*2+1))


def getLeaves(node):
    if node is None:
        return []
    if node.isLeaf:
        return [node]
    else:
        return getLeaves(node.left) + getLeaves(node.right)


def get_labels(node):
    if node is None:
        return []
    return get_labels(node.left) + get_labels(node.right) + [node.label]


def clearFprop(node, words):
    node.fprop = False


def loadTrees(dataSet='train'):
    """
    Loads training trees. Maps leaf node words to word ids.
    """
    file = 'trees/%s.txt' % dataSet
    print("Loading %s trees.." % dataSet)
    with open(file, 'r') as fid:
        trees = [Tree(l) for l in fid.readlines()]

    return trees

def simplified_data(num_train, num_dev, num_test):
    rndstate = random.getstate()
    random.seed(0)
    trees = loadTrees('train') + loadTrees('dev') + loadTrees('test')

    #filter extreme trees
    pos_trees = [t for t in trees if t.root.label==4]
    neg_trees = [t for t in trees if t.root.label==0]

    #binarize labels
    binarize_labels(pos_trees)
    binarize_labels(neg_trees)

    #split into train, dev, test
    print(len(pos_trees), len(neg_trees))
    pos_trees = sorted(pos_trees, key=lambda t: len(t.get_words()))
    neg_trees = sorted(neg_trees, key=lambda t: len(t.get_words()))
    num_train//=2
    num_dev//=2
    num_test//=2
    train = pos_trees[:num_train] + neg_trees[:num_train]
    dev = pos_trees[num_train : num_train+num_dev] + neg_trees[num_train : num_train+num_dev]
    test = pos_trees[num_train+num_dev : num_train+num_dev+num_test] + neg_trees[num_train+num_dev : num_train+num_dev+num_test]
    random.shuffle(train)
    random.shuffle(dev)
    random.shuffle(test)
    random.setstate(rndstate)


    return train, dev, test


def binarize_labels(trees):
    def binarize_node(node, _):
        if node.label<=2:
            node.label = 0
        elif node.label>2:
            node.label = 1
    for tree in trees:
        leftTraverse(tree.root, binarize_node, None)
        tree.labels = get_labels(tree.root)
