import sys, os
import numpy as np
import pandas as pd

# return a list of tuples containing all pairs of element from list1 to
# element from list2
def completeBipartitePairs(list1, list2):
    pairs = []
    for i1 in list1:
        for i2 in list2:
            for label1 in i1.label:
                for label2 in i2.label:
                    pairs.append((label1, label2))
    return pairs

class Node(object):
    def __init__(self):
        self.label = []
        self.children = []
        self.parent = None

    def __init__(self, label, parent):
        if isinstance(label, list):
            self.label = label
        else:
            self.label = []
            self.label.append(label)
        self.children = []
        self.parent = parent
        if parent != None and self not in parent.children:
            parent.children.append(self)
    
    # instance method to return a list of nodes starting from current node
    def getAllNodes(self):
        nodes = [self]
        for child in self.children:
            nodes += child.getAllNodes()
        return nodes

    # instance method to find all (ancestor, descendent) pairs from this
    # node. e.g., 1->2->3, then we have pairs (1,2), (1,3), and (2,3)
    def getAncestorDescendentPairs(self):
        pairs = []
        pairs += self.__getAncestorDescendentPairs(self)
        for child in self.children:
            pairs += child.getAncestorDescendentPairs()
        return pairs

    # helper method to getAncestorDescendentPairs
    # fix an ancestor node, find all possible descendent nodes to form a pair
    def __getAncestorDescendentPairs(self, next_node):
        pairs = []
        if next_node == None:
            return pairs
        if self != next_node:
            for label1 in self.label:
                for label2 in next_node.label:
                    #pairs += [(self.label, next_node.label)]
                    pairs += [(label1, label2)]
        for child in next_node.children:
            pairs += self.__getAncestorDescendentPairs(child)

        return pairs
    
    # instance method to get all pairs of nodes that appear in different
    # branches.
    # e.g., {a,b}, a is not an ancestor of b, nor does b to a
    def getSeparateBranchPairs(self):
        pairs = []
        pairs += self.__getSeparateBranchPairs()
        for child in self.children:
            pairs += child.getSeparateBranchPairs()
        return pairs

    # helper method to getSeparateBranchPairs
    def __getSeparateBranchPairs(self):
        # if we don't even have more than 1 child, no way to get corresponding
        # pairs
        pairs = []
        if len(self.children) < 2:
            return pairs
        
        group_list = []
        for child in self.children:
            group_list.append(child.getAllNodes())
        
        for i in range(0, len(group_list) - 1):
            for j in range(i + 1, len(group_list)):
                pairs += completeBipartitePairs(group_list[i], group_list[j])
        return pairs

    # instance method to get all pairs of labels that appear in the same node,
    # starting from the current node
    def getSameNodePairs(self):
        pairs = []
        if (len(self.label) > 1):
            for i in range(0, len(self.label) - 1):
                for j in range(i + 1, len(self.label)):
                    pairs.append((self.label[i], self.label[j]))

        for child in self.children:
            pairs += child.getSameNodePairs()
        return pairs

# read in the tree defined by the path
def readTree(path):
    root = None
    nodes = {}

    if not os.path.isfile(path):
        return None

    f = open(path, 'r')
    lines = f.read().split('\n')

    read_line = False
    for line in lines:
        if line == '':
            break
        if '#edges' in line:
            # reading line to true
            read_line = True
            continue
        if '#leaves' in line:
            read_line = False
            continue
        if read_line:
            p, c = [tuple(x.split(',')) for x in line.split(' ')]
            if p not in nodes:
                nodes[p] = Node(label=list(p), parent=None)
            if c not in nodes:
                nodes[c] = Node(label=list(c), parent=nodes[p])
            else:
                if nodes[c] not in nodes[p].children:
                    nodes[p].children.append(nodes[c])
    f.close()

    for key, node in nodes.items():
        if node.parent == None:
            if root != None:
                print("more than one root detected")
                exit()
            else:
                root = node
    return root

def evaluateTree(path, node):
    print("Path: {}".format(path))
    print("Ancestor-Descendent pairs:")
    print(node.getAncestorDescendentPairs())
    print("Different-branch pairs:")
    print(node.getSeparateBranchPairs())
    print("Same-node-label pairs:")
    print(node.getSameNodePairs())

def computeFNFP(ref_list, est_list, task):
    if task != 'ad':
        sorted_ref_list = [tuple(sorted(a)) for a in ref_list]
        sorted_est_list = [tuple(sorted(a)) for a in est_list]
        ref_dict = {k:1 for k in sorted_ref_list}
        est_dict = {k:1 for k in sorted_est_list}
        tp = [k for k in ref_dict.keys()&est_dict.keys()]
    else:
        ref_dict = {k:1 for k in ref_list}
        est_dict = {k:1 for k in est_list}
        tp = [k for k in ref_dict.keys()&est_dict.keys()]

    if len(ref_list) == 0:
        fnr = 0
    else:
        fnr = (len(ref_list) - len(tp)) / len(ref_list)
    if len(est_list) == 0:
        fpr = 0
    else:
        fpr = (len(est_list) - len(tp)) / len(est_list)
    return fnr, fpr

# compare between a reference tree and an estimated tree
# on behalf of: 1) AD pairs, 2) DB pairs, 3) SNL pairs
# Metrics: FN and FP
def compareTree(ref, est):
    # EXCEPTION: if no estimated tree (no edges), return default value
    if est == None:
        ret = [1, 0, 0, 0, 0, 0]
        if len(ref.getSeparateBranchPairs()) > 0:
            ret[2] = 1
        if len(ref.getSameNodePairs()) > 0:
            ret[4] = 1
        return ret

    # AD pairs
    ref_ad = ref.getAncestorDescendentPairs()
    est_ad = est.getAncestorDescendentPairs()
    #print(ref_ad, '\n', est_ad)
    fn_ad, fp_ad = computeFNFP(ref_ad, est_ad, 'ad')
    
    # DB pairs
    ref_db = ref.getSeparateBranchPairs()
    est_db = est.getSeparateBranchPairs()
    #print(ref_db, '\n', est_db)
    fn_db, fp_db = computeFNFP(ref_db, est_db, 'db')

    # SNL pairs
    ref_snl = ref.getSameNodePairs()
    est_snl = est.getSameNodePairs()
    #print(ref_snl, '\n', est_snl)
    fn_snl, fp_snl = computeFNFP(ref_snl, est_snl, 'snl')
    
    # return a list in the order of AD FN/FP, DB FN/FP, SNL FN/FP
    return [fn_ad, fp_ad, fn_db, fp_db, fn_snl, fp_snl]

def main():
    ## testing case
    #a = Node('a', None)
    #b = Node('b', a)
    #c = Node('c', a)
    #d = Node('d', b)
    #e = Node('e', b)
    #f = Node(['f','zzzz'], c)
    #root = a

    #print(root.getAncestorDescendentPairs())
    #print(root.getSeparateBranchPairs())
    #print(root.getSameNodePairs())

    sims = ['isa_violations']
    for sim in sims:

        # read in from each of the output (PhISCS sim1a/modified PhiSCS sim1a)
        ns = [10, 20, 40, 100]
        missing_rates = [0, 0.125, 0.25, 0.5]
        betas = [0, 0.2, 0.4]
        rep = 6
        # AD: ancestor-descendent pair
        # SNL: same-node-label pair
        # DB: different-branch pair
        columns = ['method', 'replicate', '# cells', 'missing rate', 'FN rate',
                'AD FN', 'AD FP', 'DB FN', 'DB FP', 'SNL FN', 'SNL FP']
        df_list = []

        for i in range(1, rep+1):
            print("On rep\t{}".format(i))
            # true tree path
            ref_tree_path = '/home/chengzes/Desktop/Classes/CS598MEB/'\
                    'CS598FinalProject/{}/TREES/rep{}.tre'.format(sim, i)
            ref_tree = readTree(ref_tree_path)
            #print(ref_tree.getAncestorDescendentPairs())

            for n in ns:
                for m in missing_rates:
                    # 1) PhISCS estimated tree
                    for b in betas:
                        est_tree_path = '../PhISCS/{}_output/n={}/b={}/{}/rep{}/rep{}.tre'.format(
                                    sim, n, b, m, i, i)
                        est_tree = readTree(est_tree_path)
                        row = ['PhISCS', i, n, m, b] \
                                + compareTree(ref_tree, est_tree)
                        #evaluateTree(est_tree_path, est_tree)
                        df_list.append(row)

                        # PhISCS given correct number of eliminations
                        est_tree_path = '../PhISCS/{}_givenkmax_output/n={}/b={}/{}/rep{}/rep{}.tre'.format(
                                    sim, n, b, m, i, i)
                        est_tree = readTree(est_tree_path)
                        row = ['PhISCS-given-kmax', i, n, m, b] \
                                + compareTree(ref_tree, est_tree)
                        df_list.append(row)
                    
                        # 2) modified PhISCS estimated tree
                        est_tree_path = '{}_output/n={}/b={}/{}/rep{}/rep{}.tre'.format(
                                sim, n, b, m, i, i)
                        est_tree = readTree(est_tree_path)
                        row = ['modified_PhISCS', i, n, m, b] \
                                + compareTree(ref_tree, est_tree)
                        df_list.append(row)

                        est_tree_path = '{}_p=10_output/n={}/b={}/{}/rep{}/rep{}.tre'.format(
                                sim, n, b, m, i, i)
                        est_tree = readTree(est_tree_path)
                        row = ['modified_PhISCS-p=10', i, n, m, b] \
                                + compareTree(ref_tree, est_tree)
                        df_list.append(row)
        df = pd.DataFrame(df_list, columns=columns)
        df.to_csv('benchmark/{}_benchmark.csv'.format(sim), index=False)

        avg_list = []
        avg_columns = ['method', '# cells', 'missing rate', 'FN rate',
                'AD FN', 'AD FP', 'DB FN', 'DB FP', 'SNL FN', 'SNL FP']
        data_columns = ['AD FN', 'AD FP', 'DB FN', 'DB FP', 'SNL FN', 'SNL FP']
        # calculate average error
        for n in ns:
            for m in missing_rates:
                # if PhISCS
                for b in betas:
                    row = ['PhISCS', n, m, b] \
                            + df.loc[(df['method'] == 'PhISCS') \
                            & (df['# cells'] == n) \
                            & (df['missing rate'] == m) \
                            & (df['FN rate'] == b), data_columns].mean(axis=0).tolist()
                    avg_list.append(row)

                    row = ['PhISCS-given-kmax', n, m, b] \
                            + df.loc[(df['method'] == 'PhISCS-given-kmax') \
                            & (df['# cells'] == n) \
                            & (df['missing rate'] == m) \
                            & (df['FN rate'] == b), data_columns].mean(axis=0).tolist()
                    avg_list.append(row)

                    row = ['modified_PhISCS', n, m, b] \
                        + df.loc[(df['method'] == 'modified_PhISCS') \
                        & (df['# cells'] == n) \
                        & (df['missing rate'] == m) \
                        & (df['FN rate'] == b), data_columns].mean(axis=0).tolist()
                    avg_list.append(row)

                    row = ['modified_PhISCS-p=10', n, m, b] \
                        + df.loc[(df['method'] == 'modified_PhISCS') \
                        & (df['# cells'] == n) \
                        & (df['missing rate'] == m) \
                        & (df['FN rate'] == b), data_columns].mean(axis=0).tolist()
                    avg_list.append(row)
        avg_df = pd.DataFrame(avg_list, columns=avg_columns)
        avg_df = avg_df.round(3)
        avg_df.to_csv('benchmark/{}_average_error.csv'.format(sim), index=False)
if __name__ == "__main__":
    main()
