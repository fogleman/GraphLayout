import layout
import render
import wx

def create_bitmap(path, size, edges):
    app = wx.App(None)
    nodes = layout.layout(edges)
    bitmap = render.render(size, edges, nodes)
    bitmap.SaveFile(path, wx.BITMAP_TYPE_PNG)

if __name__ == '__main__':
    path = 'output.png'
    size = 800
    edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 4), (2, 5), (3, 6)]
    create_bitmap(path, size, edges)
