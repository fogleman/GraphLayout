from itertools import combinations
from math import hypot
import anneal
import random

SEPARATE = 0
INTERSECT = 1
OVERLAP = 2

def project(x0, y0, x1, y1, x2, y2):
    xt = None
    yt = None
    if x0 != x1:
        xt = float(x2 - x0) / (x1 - x0)
    elif x2 != x0:
        return None
    if y0 != y1:
        yt = float(y2 - y0) / (y1 - y0)
    elif y2 != y0:
        return None
    if xt is None:
        return yt
    if yt is None:
        return xt
    if xt == yt:
        return xt
    return None

def segments_intersect(x0, y0, x1, y1, x2, y2, x3, y3):
    p1, q1 = x1 - x0, y1 - y0
    p2, q2 = x3 - x2, y3 - y2
    det = float(-p2 * q1 + p1 * q2)
    if det == 0:
        a = project(x0, y0, x1, y1, x2, y2)
        b = project(x0, y0, x1, y1, x3, y3)
        c = project(x2, y2, x3, y3, x0, y0)
        d = project(x2, y2, x3, y3, x1, y1)
        for x in [a, b, c, d]:
            if x > 0 and x < 1:
                return OVERLAP
        return SEPARATE
    s = (-q1 * (x0 - x2) + p1 * (y0 - y2)) / det
    t = ( p2 * (y0 - y2) - q2 * (x0 - x2)) / det
    if s > 0 and s < 1 and t > 0 and t < 1:
        return INTERSECT
    return SEPARATE

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
        # count intersecting edges
        intersecting_edges = 0
        overlapping_edges = 0
        for (s1, t1), (s2, t2) in combinations(self.edges, 2):
            s1, t1, s2, t2 = [self.nodes[x] for x in [s1, t1, s2, t2]]
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = s1, t1, s2, t2
            result = segments_intersect(x0, y0, x1, y1, x2, y2, x3, y3)
            if result == INTERSECT:
                intersecting_edges += 1
            if result == OVERLAP:
                overlapping_edges += 1
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
        # debug output
        if debug:
            print 'intersecting_nodes:', intersecting_nodes
            print 'overlapping_edges:', overlapping_edges
            print 'intersecting_edges:', intersecting_edges
            print 'non_orthogonal_edges:', non_orthogonal_edges
            print 'total_edge_length:', total_edge_length    
        # compute score
        result = 0
        result += intersecting_nodes * 100
        result += overlapping_edges * 100
        result += intersecting_edges * 50
        result += non_orthogonal_edges * 10
        result += total_edge_length
        return result
    def do_move(self):
        key = random.choice(self.nodes.keys())
        x = random.randint(0, 9)
        y = random.randint(0, 9)
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
        print energy
    state = Model(edges)
    annealer = anneal.Annealer(energy, do_move, undo_move, make_copy, listener)
    state, energy = annealer.anneal(state, 100, 1, 100000)
    return state
