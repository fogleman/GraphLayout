#include <math.h>
#include <stdio.h>
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
    float node_node;
    float node_edge;
    float edge_edge;
    float rank;
    float length;
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

float distance(float x0, float y0, float x1, float y1) {
    return hypot(x1 - x0, y1 - y0);
}

float dot(float x0, float y0, float x1, float y1, float x2, float y2) {
    return (x1 - x0) * (x2 - x1) + (y1 - y0) * (y2 - y1);
}

float cross(float x0, float y0, float x1, float y1, float x2, float y2) {
    return (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0);
}

float segment_point_distance(
    float x0, float y0, float x1, float y1, float x2, float y2)
{
    if (x0 == x1 && y0 == y1) {
        return distance(x0, y0, x2, y2);
    }
    float d1 = dot(x0, y0, x1, y1, x2, y2);
    if (d1 > 0) {
        return distance(x1, y1, x2, y2);
    }
    float d2 = dot(x1, y1, x0, y0, x2, y2);
    if (d2 > 0) {
        return distance(x0, y0, x2, y2);
    }
    return fabs(cross(x0, y0, x1, y1, x2, y2) / distance(x0, y0, x1, y1));
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
    int node_node = 0;
    for (int i = 0; i < model->node_count; i++) {
        for (int j = i + 1; j < model->node_count; j++) {
            Node *a = &model->nodes[i];
            Node *b = &model->nodes[j];
            if (distance(a->x, a->y, b->x, b->y) < 1) {
                node_node++;
            }
        }
    }
    // count nodes on edges
    int node_edge = 0;
    for (int i = 0; i < model->edge_count; i++) {
        Edge *edge = &model->edges[i];
        Node *a = &model->nodes[edge->a];
        Node *b = &model->nodes[edge->b];
        for (int j = 0; j < model->node_count; j++) {
            Node *c = &model->nodes[j];
            if (c == a || c == b) {
                continue;
            }
            if (segment_point_distance(
                a->x, a->y, b->x, b->y, c->x, c->y) < 0.25)
            {
                node_edge++;
            }
        }
    }
    // count intersecting edges
    int edge_edge = 0;
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
                edge_edge++;
            }
        }
    }
    // check node ranks
    int rank = 0;
    for (int i = 0; i < model->node_count; i++) {
        Node *a = &model->nodes[i];
        if (a->rank == 0) {
            continue;
        }
        for (int j = i + 1; j < model->node_count; j++) {
            Node *b = &model->nodes[j];
            if (a->rank >= b->rank && a->y < b->y) {
                rank++;
            }
            if (a->rank <= b->rank && a->y > b->y) {
                rank++;
            }
        }
    }
    // sum edge lengths
    float length = 0;
    for (int i = 0; i < model->edge_count; i++) {
        Edge *edge = &model->edges[i];
        Node *a = &model->nodes[edge->a];
        Node *b = &model->nodes[edge->b];
        length += distance(a->x, a->y, b->x, b->y);
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
    attrib->node_node = node_node;
    attrib->node_edge = node_edge;
    attrib->edge_edge = edge_edge;
    attrib->rank = rank;
    attrib->length = length;
    attrib->area = area;
}

void print_attrib(Model *model) {
    Attrib attrib;
    analyze(model, &attrib);
    printf("node_node: %g\n", attrib.node_node);
    printf("node_edge: %g\n", attrib.node_edge);
    printf("edge_edge: %g\n", attrib.edge_edge);
    printf("rank: %g\n", attrib.rank);
    printf("length: %g\n", attrib.length);
    printf("area: %g\n", attrib.area);
    printf("\n");
}

float energy(Model *model, Attrib *weights) {
    Attrib _attrib;
    Attrib *attrib = &_attrib;
    analyze(model, attrib);
    float result = 0;
    result += attrib->node_node * weights->node_node;
    result += attrib->node_edge * weights->node_edge;
    result += attrib->edge_edge * weights->edge_edge;
    result += attrib->rank * weights->rank;
    result += attrib->length * weights->length;
    result += attrib->area * weights->area;
    return result;
}

void do_move(Model *model, Undo *undo) {
    int index = rand_int(model->node_count);
    Node *node = &model->nodes[index];
    undo->index = index;
    undo->x = node->x;
    undo->y = node->y;
    node->x = rand_int(10) / 2.0;
    node->y = rand_int(10) / 2.0;
    // float dx, dy;
    // do {
    //     dx = (rand_int(3) - 1) / 2.0;
    //     dy = (rand_int(3) - 1) / 2.0;
    // } while (dx == 0 && dy == 0);
    // node->x += dx;
    // node->y += dy;
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

void randomize(Model *model) {
    int size = ceilf(sqrtf(model->node_count));
    for (int i = 0; i < model->node_count; i++) {
        Node *node = &model->nodes[i];
        node->x = rand_int(size);
        node->y = rand_int(size);
    }
}

void random_start(Model *model, Attrib *weights, int steps) {
    Model best;
    float current_energy = energy(model, weights);
    float best_energy = current_energy;
    copy(&best, model);
    for (int step = 0; step < steps; step++) {
        randomize(model);
        current_energy = energy(model, weights);
        if (current_energy < best_energy) {
            best_energy = current_energy;
            copy(&best, model);
        }
    }
    copy(model, &best);
}

float anneal(
    Model *model, Attrib *weights, float max_temp, float min_temp,
    int steps, callback_func func)
{
    Model best;
    Undo undo;
    srand(0);
    random_start(model, weights, 1000);
    float factor = -log(max_temp / min_temp);
    float current_energy = energy(model, weights);
    float previous_energy = current_energy;
    float best_energy = current_energy;
    copy(&best, model);
    func(&best, best_energy);
    for (int step = 0; step < steps; step++) {
        float temp = max_temp * exp(factor * step / steps);
        do_move(model, &undo);
        current_energy = energy(model, weights);
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
    print_attrib(model);
    return best_energy;
}
