from itertools import combinations
from math import hypot
import anneal
import random

def point_on_segment(x0, y0, x1, y1, x2, y2):
    xt = None
    yt = None
    if x0 != x1:
        xt = float(x2 - x0) / (x1 - x0)
    elif x2 != x0:
        return False
    if y0 != y1:
        yt = float(y2 - y0) / (y1 - y0)
    elif y2 != y0:
        return False
    if xt is None:
        t = yt
    elif yt is None:
        t = xt
    elif xt == yt:
        t = xt
    else:
        return False
    return t > 0 and t < 1

def segments_intersect(x0, y0, x1, y1, x2, y2, x3, y3):
    p1, q1 = x1 - x0, y1 - y0
    p2, q2 = x3 - x2, y3 - y2
    det = float(-p2 * q1 + p1 * q2)
    if det == 0:
        return False
    s = (p1 * (y0 - y2) - q1 * (x0 - x2)) / det
    t = (p2 * (y0 - y2) - q2 * (x0 - x2)) / det
    return s > 0 and s < 1 and t > 0 and t < 1

class Model(object):
    def __init__(self, edges):
        nodes = {}
        for a, b in edges:
            nodes[a] = (0, 0)
            nodes[b] = (0, 0)
        self.edges = edges
        self.nodes = nodes
    def energy(self, debug=False):
        # count intersecting nodes
        intersecting_nodes = 0
        for (x1, y1), (x2, y2) in combinations(self.nodes.values(), 2):
            if hypot(x2 - x1, y2 - y1) < 1:
                intersecting_nodes += 1
        # count nodes on edges
        nodes_on_edges = 0
        for a, b in self.edges:
            a, b = [self.nodes[x] for x in [a, b]]
            (x1, y1), (x2, y2) = a, b
            for x, y in self.nodes.values():
                if point_on_segment(x1, y1, x2, y2, x, y):
                    nodes_on_edges += 1
        # count intersecting edges
        intersecting_edges = 0
        for (s1, t1), (s2, t2) in combinations(self.edges, 2):
            s1, t1, s2, t2 = [self.nodes[x] for x in [s1, t1, s2, t2]]
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = s1, t1, s2, t2
            if segments_intersect(x0, y0, x1, y1, x2, y2, x3, y3):
                intersecting_edges += 1
        # check edge lengths and orthogonality
        total_edge_length = 0
        non_orthogonal_edges = len(self.edges)
        for a, b in self.edges:
            a, b = [self.nodes[x] for x in [a, b]]
            (x1, y1), (x2, y2) = a, b
            length = hypot(x2 - x1, y2 - y1)
            total_edge_length += length
            if x1 == x2 or y1 == y2:
                non_orthogonal_edges -= 1
        # compute score
        result = 0
        result += intersecting_nodes * 100
        result += nodes_on_edges * 100
        result += intersecting_edges * 50
        #result += non_orthogonal_edges * 10
        result += total_edge_length
        # debug output
        if debug:
            print 'intersecting_nodes:', intersecting_nodes
            print 'nodes_on_edges:', nodes_on_edges
            print 'intersecting_edges:', intersecting_edges
            print 'non_orthogonal_edges:', non_orthogonal_edges
            print 'total_edge_length:', total_edge_length
            print 'energy:', result
        return result
    def do_move(self):
        key = random.choice(self.nodes.keys())
        if random.randint(0, 1):
            x, y = self.nodes[key]
            x += random.randint(-1, 1)
            y += random.randint(-1, 1)
        else:
            x = random.randint(0, 5)
            y = random.randint(0, 5)
        result = (key, self.nodes[key])
        self.nodes[key] = (x, y)
        return result
    def undo_move(self, undo_data):
        key, value = undo_data
        self.nodes[key] = value

def layout(edges):
    def energy(state):
        return state.energy()
    def do_move(state):
        return state.do_move()
    def undo_move(state, undo_data):
        state.undo_move(undo_data)
    def make_copy(state):
        result = Model(state.edges)
        result.nodes = dict(state.nodes)
        return result
    def listener(state, energy):
        state.energy(True) # prints debug output
        print
    state = Model(edges)
    annealer = anneal.Annealer(energy, do_move, undo_move, make_copy, listener)
    state, energy = annealer.anneal(state, 100, 0.1, 100000)
    return state
