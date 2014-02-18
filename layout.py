from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, c_float, c_int, byref

dll = CDLL('_layout.so')

MAX_EDGES = 128
MAX_NODES = 128

WEIGHTS = {
    'node_node': 100,
    'node_edge': 100,
    'edge_edge': 10,
    'rank': 5,
    'length': 1,
    'area': 1,
}

class Node(Structure):
    _fields_ = [
        ('rank', c_int),
        ('x', c_float),
        ('y', c_float),
    ]

class Edge(Structure):
    _fields_ = [
        ('a', c_int),
        ('b', c_int),
    ]

class Model(Structure):
    _fields_ = [
        ('edge_count', c_int),
        ('node_count', c_int),
        ('edges', Edge * MAX_EDGES),
        ('nodes', Node * MAX_NODES),
    ]

class Attrib(Structure):
    _fields_ = [
        ('node_node', c_float),
        ('node_edge', c_float),
        ('edge_edge', c_float),
        ('rank', c_float),
        ('length', c_float),
        ('area', c_float),
    ]

CALLBACK_FUNC = CFUNCTYPE(None, POINTER(Model), c_float)

dll.anneal.restype = c_float
dll.anneal.argtypes = [
    POINTER(Model), POINTER(Attrib),
    c_float, c_float, c_int, CALLBACK_FUNC]

def anneal(model, weights, max_temp, min_temp, steps, callback_func):
    return dll.anneal(
        byref(model), byref(weights),
        max_temp, min_temp, steps, CALLBACK_FUNC(callback_func))

def cyclic(nodes, inputs):
    remaining = set(nodes)
    while remaining:
        count = 0
        for node in nodes:
            if node not in remaining:
                continue
            if remaining & inputs[node]:
                continue
            count += 1
            remaining.remove(node)
        if count == 0:
            return True
    return False

def rank(inputs, node, memo=None):
    memo = memo or {}
    if node in memo:
        return memo[node]
    elif inputs[node]:
        result = min(rank(inputs, x, memo) for x in inputs[node]) + 1
    else:
        result = 1
    memo[node] = result
    return result

def topographical_sort(nodes, inputs):
    if cyclic(nodes, inputs):
        ranks = [0] * len(nodes)
    else:
        memo = {}
        ranks = [rank(inputs, node, memo) for node in nodes]
    return sorted(zip(ranks, nodes))

def create_model(edges):
    nodes = set()
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)
    nodes = sorted(nodes)
    inputs = dict((x, set()) for x in nodes)
    outputs = dict((x, set()) for x in nodes)
    for a, b in edges:
        inputs[b].add(a)
        outputs[a].add(b)
    topo = topographical_sort(nodes, inputs)
    ranks = dict((node, rank) for rank, node in topo)
    lookup = dict((node, index) for index, node in enumerate(nodes))
    model = Model()
    model.edge_count = len(edges)
    model.node_count = len(nodes)
    for index, node in enumerate(nodes):
        model.nodes[index].rank = ranks[node]
        model.nodes[index].x = 0
        model.nodes[index].y = 0
    for index, (a, b) in enumerate(edges):
        model.edges[index].a = lookup[a]
        model.edges[index].b = lookup[b]
    return model, lookup

def create_attrib(data):
    keys = [
        'node_node',
        'node_edge',
        'edge_edge',
        'rank',
        'length',
        'area',
    ]
    result = Attrib()
    for key in keys:
        setattr(result, key, data.get(key, WEIGHTS[key]))
    return result

def layout(edges, weights=None, steps=100000, listener=None):
    model, lookup = create_model(edges)
    weights = create_attrib(weights or {})
    def create_result(model):
        nodes = {}
        for key, index in lookup.items():
            node = model.nodes[index]
            nodes[key] = (node.x, node.y)
        return nodes
    def callback_func(model, energy):
        if listener is not None:
            result = create_result(model.contents)
            listener(result, energy)
    anneal(model, weights, 100, 0.1, steps, callback_func)
    return create_result(model)
