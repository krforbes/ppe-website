import pandas as pd
import numpy as np
import math
import random
import time



# Parameters for searching
# If any of these limits are reached the code stops with however many matchings it found.
# might be optional now 
time_limit = 300 # Max time in seconds
match_limit = 15 # Stops after this many unique matchings are found
repetition_limit = 50 # Stops if you get this many consecutive valid matchings with no new ones found



class Node: 
  def __init__(self, name, isPerson, difficulty = None):
    self.name = name
    self.isPerson = isPerson
    self.difficulty = difficulty
    self.adj = [] 
    # The following 2 parameters will change each time a partial matching object is created
    # so can't really be trusted outside of that context
    self.match = None 
    self.dist = None


class Matching: 
    def __init__(self, data, hard = 'expHard', multiple = 'expMultiple'):
        # takes in a formatted dataframe 
        pieces = list(data.columns[4:])
        people = list(data.index[2:])
        # Create the original graph - these are global variables! 
        left = [Node(person, True) for person in people] # a list for graph matching algorithm
        leftST = {} # same nodes but as a symbol table indexed by name, to create the edges
        for i in range(len(people)):
            leftST[people[i]] = left[i] 

        right = []
        for piece in pieces:
            hard_parts = [Node(piece, False, 'hard') for i in range(data.at['hard parts', piece])]
            easy_parts = [Node(piece, False, 'easy') for i in range(data.at['easy parts', piece])]
            right += hard_parts + easy_parts# add to the right side of the graph
            for person in people:
                if data.at[person, piece] == 1: # if they want to play this piece
                    if data.at[person, hard]: # if they are willing to play hard part
                        for node in hard_parts:
                            node.adj.append(leftST[person])
                            leftST[person].adj.append(node)
                    for node in easy_parts: # everyone can play easy parts
                        node.adj.append(leftST[person])
                        leftST[person].adj.append(node)
        

        null = Node('null', False) # fake node for algorithm, connected to right
        for r in right:
            r.adj.append(null)
            null.adj.append(r)
        self.left = left
        self.right = right
        self.null = null
        self.people = people
        self.pieces = pieces
        self.hard = hard
        self.data = data
        self.multiple = multiple 

    def match_all(self):
        first = PartialMatching(self.left, self.right, self.null, self)
        (left2, right2, null2) = first.remaining_graph()
        second = PartialMatching(left2, right2, null2, self)
        pairs = first.pairs + second.pairs
        # if len(pairs) < len(self.right): # if not completely matched it doesn't count.
        #    # print(len(self.right)-len(pairs), 'problems')
        #     return None
        return pairs

    # if you shuffle the order everything is considered in, you (probably) get a 
    # different matching. we do this because trying every possibility would take forever
    def shuffle(self,random_state = None):
        if random_state is not None:
            random.seed(random_state)
        random.shuffle(self.left)
        random.shuffle(self.right)
        for l in self.left:
            random.shuffle(l.adj)
        for r in self.right:
            random.shuffle(r.adj)


class PartialMatching: # only matches 1 part per person, but can return new graph for second round. 
# https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm

    def __init__(self, left, right, null, matching):
        self.left = left
        self.null = null
        self.right = right
        self.assignments = {} # 2 way node ST
        self.pairs = [] # list of pairs, in string format, names only not nodes. 
        self.matching = matching

        # Reset matchings of nodes to do this one.
        for l in left:
            l.match = null # the matchings in the objects change from multiple function calls, self.pairs is the result of this one.
            l.dist = 0
        for r in right:
            r.match = null
            r.dist = 0
        null.dist = 0

        # Run HK algorithm to generate matching
        self.size = 0
        while self.bfs():
            for l in left:
                if l.match == null:
                    if self.dfs(l):
                        self.size += 1

        # Construct self.pairs now that matches are finalized
        for l in self.assignments:
            if l in left:
                r = self.assignments[l]
                self.pairs.append((r.name, l.name))
    
    def bfs(self): # this is modified bfs
        queue = [] # we're pretending this list is a queue because python 
        for l in self.left:
            if l.match == self.null:
                l.dist = 0
                queue.append(l)
            else:
                l.dist = math.inf  
        self.null.dist = math.inf
        while len(queue) > 0:
            l = queue.pop(0)
            if l.dist < self.null.dist:
                for r in l.adj:
                    if r.match.dist == math.inf:
                        r.match.dist = l.dist + 1
                        queue.append(r.match)
        return self.null.dist != math.inf 

    def dfs(self,l):
        if l != self.null:
            for r in l.adj:
                if r.match.dist == l.dist + 1:
                    if self.dfs(r.match):
                        r.match = l
                        l.match = r
                        self.assignments[r] = l
                        self.assignments[l] = r
                        return True
            l.dist = math.inf
            return False
        return True

    def remaining_graph(self): # copy of subgraph with parts left over and people 
        # who want to play multiple pieces
        null2 = Node('null', False)
        left2 = [Node(person, True) for person in self.matching.people if self.matching.data.at[person, self.matching.multiple] == 1]
        leftST2 = {} 
        for l in left2:
            leftST2[l.name] = l
        right2 = [] # parts without a person yet
        for r in self.right:
            if r not in self.assignments:
                r2 = Node(r.name, False, r.difficulty)
                right2.append(r2)
                for l in r.adj: # l.name in leftST2 excludes the old null. 
                    if l.name in leftST2 and self.assignments[l].name != r.name: # you can't play multiple parts from the same piece
                        r2.adj.append(leftST2[l.name]) # new nodes same names.
                        leftST2[l.name].adj.append(r2)
                r2.adj.append(null2)
                null2.adj.append(r2)
        return (left2, right2, null2)





# test using the original program and fall 2022 preferences
'''
test_data = pd.read_csv("test-data-fall.csv", index_col = 'name')
m = Matching(test_data, 'expHard', 'expMultiple')

start = time.time()
matches = []
repetitions = 0

while time.time() - start < time_limit and len(matches) < match_limit and repetitions < repetition_limit:
  m.shuffle()
  matching = m.match_all()
  if matching is None:
    continue
  repetitions += 1
  string = ''
  for piece in m.pieces:
    string += piece + ": "
    group = []
    for pair in matching:
      if pair[0] == piece:
        group.append(pair[1])
    group.sort()
    for person in group:
      string += person + ', '
    string += ';' # this was going to be a newline but newline is broken??? so split to print later
  if string not in matches:
    matches.append(string)
    repetitions = 0


for match in matches:
  for string in match.split(';'):
    print(string)'''