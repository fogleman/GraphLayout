## GraphLayout

Graph drawing using simulated annealing for layout.

### Input

    path = 'output.png'
    size = 800
    edges = [
        (1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 6),
        (4, 3), (4, 6), (4, 7), (5, 4), (5, 7), (7, 6),
    ]
    create_bitmap(path, size, edges)

### Output

![Screenshot](http://i.imgur.com/4TP0gRM.png)
