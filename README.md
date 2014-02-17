## GraphLayout

Graph drawing using simulated annealing for layout.

### Input

    edges = [
        (5, 11),
        (11, 10),
        (11, 2),
        (3, 10),
        (3, 8),
        (8, 9),
        (11, 9),
        (7, 8),
        (7, 11),
    ]
    model = graph.layout(edges)
    bitmap = render(model, 800)

### Output

![Screenshot](http://i.imgur.com/tR6fPCJ.png)
