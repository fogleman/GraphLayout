import layout
import render
import wx

def create_bitmap(path, max_width, max_height, edges):
    app = wx.App(None)
    nodes = layout.layout(edges)
    bitmap = render.render(max_width, max_height, edges, nodes)
    bitmap.SaveFile(path, wx.BITMAP_TYPE_PNG)

if __name__ == '__main__':
    path = 'output.png'
    size = 800
    edges = [
        (1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 6),
        (4, 3), (4, 6), (4, 7), (5, 4), (5, 7), (7, 6),
    ]
    create_bitmap(path, size, size, edges)
