#include <math.h>
#include <stdlib.h>
#include <string.h>

#define MAX_EDGES 128
#define MAX_NODES 128

#define INF 1e9
#define EPS 1e-9

#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

typedef struct {
    int rank;
    float x;
    float y;
} Node;

typedef struct {
    int a;
    int b;
} Edge;

typedef struct {
    int edge_count;
    int node_count;
    Edge edges[MAX_EDGES];
    Node nodes[MAX_NODES];
} Model;

typedef struct {
    int index;
    float x;
    float y;
} Undo;

typedef struct {
    int intersecting_nodes;
    int nodes_on_edges;
    int intersecting_edges;
    int out_of_rank_nodes;
    float total_edge_length;
    float area;
} Attrib;

typedef void (*callback_func)(Model *, float);

int rand_int(int n) {
    int result;
    while (n <= (result = rand() / (RAND_MAX / n)));
    return result;
}

float rand_float() {
    return (float)rand() / (float)RAND_MAX;
}

int point_on_segment(
    float x0, float y0, float x1, float y1,
    float x2, float y2)
{
    float xt = INF;
    float yt = INF;
    if (x0 != x1) {
        xt = (x2 - x0) / (x1 - x0);
    }
    else if (x2 != x0) {
        return 0;
    }
    if (y0 != y1) {
        yt = (y2 - y0) / (y1 - y0);
    }
    else if (y2 != y0) {
        return 0;
    }
    float t = INF;
    if (xt == INF) {
        t = yt;
    }
    else if (yt == INF) {
        t = xt;
    }
    else if (abs(xt - yt) < EPS) {
        t = xt;
    }
    else {
        return 0;
    }
    return t > 0 && t < 1;
}

int segments_intersect(
    float x0, float y0, float x1, float y1,
    float x2, float y2, float x3, float y3)
{
    float p1 = x1 - x0;
    float q1 = y1 - y0;
    float p2 = x3 - x2;
    float q2 = y3 - y2;
    float det = p1 * q2 - p2 * q1;
    if (det == 0) {
        return 0;
    }
    float s = (p1 * (y0 - y2) - q1 * (x0 - x2)) / det;
    float t = (p2 * (y0 - y2) - q2 * (x0 - x2)) / det;
    return s > 0 && s < 1 && t > 0 && t < 1;
}

void analyze(Model *model, Attrib* attrib) {
    // count intersecting nodes
    int intersecting_nodes = 0;
    for (int i = 0; i < model->node_count; i++) {
        for (int j = i + 1; j < model->node_count; j++) {
            Node *a = &model->nodes[i];
            Node *b = &model->nodes[j];
            if (a->x == b->x && a->y == b->y) {
                intersecting_nodes++;
            }
            // if (hypot(a->x - b->x, a->y - b->y) < 1) {
            //     intersecting_nodes++;
            // }
        }
    }
    // check node ranks
    int out_of_rank_nodes = 0;
    for (int i = 0; i < model->node_count; i++) {
        Node *a = &model->nodes[i];
        if (a->rank == 0) {
            continue;
        }
        for (int j = i + 1; j < model->node_count; j++) {
            Node *b = &model->nodes[j];
            if (a->rank >= b->rank && a->y < b->y) {
                out_of_rank_nodes++;
            }
            if (a->rank <= b->rank && a->y > b->y) {
                out_of_rank_nodes++;
            }
        }
    }
    // count nodes on edges
    int nodes_on_edges = 0;
    for (int i = 0; i < model->edge_count; i++) {
        Edge *edge = &model->edges[i];
        Node *a = &model->nodes[edge->a];
        Node *b = &model->nodes[edge->b];
        for (int j = 0; j < model->node_count; j++) {
            Node *c = &model->nodes[j];
            if (point_on_segment(a->x, a->y, b->x, b->y, c->x, c->y)) {
                nodes_on_edges++;
            }
        }
    }
    // count intersecting edges
    int intersecting_edges = 0;
    for (int i = 0; i < model->edge_count; i++) {
        for (int j = i + 1; j < model->edge_count; j++) {
            Edge *p = &model->edges[i];
            Edge *q = &model->edges[j];
            Node *a = &model->nodes[p->a];
            Node *b = &model->nodes[p->b];
            Node *c = &model->nodes[q->a];
            Node *d = &model->nodes[q->b];
            if (segments_intersect(
                a->x, a->y, b->x, b->y, c->x, c->y, d->x, d->y))
            {
                intersecting_edges++;
            }
        }
    }
    // sum edge lengths
    float total_edge_length = 0;
    for (int i = 0; i < model->edge_count; i++) {
        Edge *edge = &model->edges[i];
        Node *a = &model->nodes[edge->a];
        Node *b = &model->nodes[edge->b];
        total_edge_length += hypot(a->x - b->x, a->y - b->y);
    }
    // compute graph area
    Node *node = &model->nodes[0];
    float minx = node->x;
    float miny = node->y;
    float maxx = node->x;
    float maxy = node->y;
    for (int i = 1; i < model->node_count; i++) {
        Node *node = &model->nodes[i];
        minx = MIN(minx, node->x);
        miny = MIN(miny, node->y);
        maxx = MAX(maxx, node->x);
        maxy = MAX(maxy, node->y);
    }
    float area = (maxx - minx) * (maxy - miny);
    // result
    attrib->intersecting_nodes = intersecting_nodes;
    attrib->nodes_on_edges = nodes_on_edges;
    attrib->intersecting_edges = intersecting_edges;
    attrib->out_of_rank_nodes = out_of_rank_nodes;
    attrib->total_edge_length = total_edge_length;
    attrib->area = area;
}

float energy(Model *model) {
    Attrib attrib;
    analyze(model, &attrib);
    float result = 0;
    result += attrib.intersecting_nodes * 100;
    result += attrib.nodes_on_edges * 100;
    result += attrib.intersecting_edges * 10;
    result += attrib.out_of_rank_nodes * 10;
    result += attrib.total_edge_length;
    result += attrib.area * 0.1;
    return result;
}

void do_move(Model *model, Undo *undo) {
    int index = rand_int(model->node_count);
    Node *node = &model->nodes[index];
    undo->index = index;
    undo->x = node->x;
    undo->y = node->y;
    node->x = rand_int(6);
    node->y = rand_int(6);
}

void undo_move(Model *model, Undo *undo) {
    Node *node = &model->nodes[undo->index];
    node->x = undo->x;
    node->y = undo->y;
}

void copy(Model *dst, Model *src) {
    dst->edge_count = src->edge_count;
    dst->node_count = src->node_count;
    memcpy(dst->edges, src->edges, sizeof(Edge) * src->edge_count);
    memcpy(dst->nodes, src->nodes, sizeof(Node) * src->node_count);
}

float anneal(
    Model *model, float max_temp, float min_temp,
    int steps, callback_func func)
{
    Model best;
    Undo undo;
    srand(0);
    float factor = -log(max_temp / min_temp);
    float current_energy = energy(model);
    float previous_energy = current_energy;
    float best_energy = current_energy;
    copy(&best, model);
    func(&best, best_energy);
    for (int step = 0; step < steps; step++) {
        float temp = max_temp * exp(factor * step / steps);
        do_move(model, &undo);
        current_energy = energy(model);
        float change = current_energy - previous_energy;
        if (change > 0 && exp(-change / temp) < rand_float()) {
            undo_move(model, &undo);
        }
        else {
            previous_energy = current_energy;
            if (current_energy < best_energy) {
                best_energy = current_energy;
                copy(&best, model);
                func(&best, best_energy);
                if (current_energy <= 0) {
                    break;
                }
            }
        }
    }
    copy(model, &best);
    return best_energy;
}
