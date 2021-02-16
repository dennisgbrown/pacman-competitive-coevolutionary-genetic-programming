# -*- coding: utf-8 -*-
import random
import sys

sys.path.append('code')


class ExprTree():
    """
    Defines an Expression Tree -- this is the encoding of an individual.
    """
    def __init__(self, root):
        self.root = root
        self.fitness = -1  # fitness may be modified by parsimony pressure
        self.score = -1
        self.world_data = []  # the world data that produced the fitness

    # Canonical list of terminals for Pac supported by the Expression Tree class
    pac_terminals = ['G', 'P', 'W', 'F', 'constant']

    # Canonical list of terminals for Ghost supported by the Expression Tree class
    ghost_terminals = ['G', 'P', 'W', 'F', 'M', 'constant']

    # Canonical list of functions supported by the Expression Tree class
    functions = ['+', '-', '*', '/', 'RAND']


class Node():
    """
    Defines a node in an ExprTree.
    """
    def __init__(self, expr = None, left = None, right = None,
                 constant = 0):
        self.expr = expr
        self.left = left
        self.right = right
        self.constant = constant
        self.parent = None
        self.depth = 0
        self.height = 0
        self.size = 1


    def calc(self, gpwfm):
        """
        Return the recursively-calculated numerical value represented by
        this node.

        gpwf is a list containing the values of G, P, W, and F so we
        don't have to recalculate them each time they are encountered
        in the tree.
        """
        # If this is an input node (leaf node) return a value.
        if (self.expr == 'G'): return gpwfm[0]
        if (self.expr == 'P'): return gpwfm[1]
        if (self.expr == 'W'): return gpwfm[2]
        if (self.expr == 'F'): return gpwfm[3]
        if (self.expr == 'M'): return gpwfm[4]
        if (self.expr == 'constant'): return self.constant

        # Calculate values of left and right children.
        left_val = self.left.calc(gpwfm)
        right_val = self.right.calc(gpwfm)

        # Apply the appropriate function to the child values and return it.
        if (self.expr == '+'): return left_val + right_val
        if (self.expr == '-'): return left_val - right_val
        if (self.expr == '*'): return left_val * right_val
        if (self.expr == '/'):
            if (right_val == 0): return 0  # lazy way to deal with divide-by-zero
            else: return left_val / right_val
        if (self.expr == 'RAND'):
            return random.uniform(left_val, right_val)


    def reset_metrics(self, parent = None, depth = 0):
        """
        Recursive method to reset depth, height, and size of all nodes.
        """
        self.parent = parent
        self.depth = depth
        self.height = 0
        self.size = 1
        if (self.expr in ExprTree.functions):
            self.left.reset_metrics(parent = self, depth = self.depth + 1)
            self.right.reset_metrics(parent = self, depth = self.depth + 1)
            self.size += (self.left.size + self.right.size)
            self.height = 1 + max(self.left.height, self.right.height)


    def find_nth_node(self, n, counter = 1):
        """
        Use breadth-first-search to identify and return the "nth"
        node of the tree.
        """
        # Sanity check
        if (n > self.size):
            print("find_nth_node error: n > size:", n)
            sys.exit(1)

        # Visit nodes with BFS, incrementing counter until we find a match
        to_visit = [self]
        counter = 0
        while (len(to_visit) > 0):
            curr = to_visit.pop(0)
            counter += 1
            if (counter == n):
                return curr
            if (curr.expr in ExprTree.functions):
                to_visit.append(curr.left)
                to_visit.append(curr.right)


    def copy(self, node):
        """
        Copy values from given node to this node
        """
        self.expr = node.expr
        self.left = node.left
        self.right = node.right
        self.constant = node.constant
        self.parent = node.parent
        self.depth = node.depth
        self.height = node.height
        self.size = node.size


    def repr_helper(self, level):
        """
        Return a string representing this node.

        level = depth of this node, for printing the pipe indents
        """

        # If input (leaf) node, return string representing input.
        if (self.expr in ['G', 'P', 'W', 'F', 'M', 'constant']):
            if (self.expr == 'constant'):
                return ('|' * level) + str(self.constant) + '\n'
            else:
                return ('|' * level) + self.expr + '\n'

        # If operator node, return a recursively-generated string.
        else:
            return ('|' * level) + self.expr + '\n' \
                + self.left.repr_helper(level + 1) \
                + self.right.repr_helper(level + 1)


    def __repr__(self):
        """
        Return a string representing this node.
        """
        return self.repr_helper(0)
