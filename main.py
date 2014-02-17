from math import atan2, cos, sin, pi
import graph
import wx

def render(model, size):
    app = wx.App(None)
    padding = 1
    positions = model.nodes.values()
    x1 = min(x for x, y in positions) - padding
    y1 = min(y for x, y in positions) - padding
    x2 = max(x for x, y in positions) + padding
    y2 = max(y for x, y in positions) + padding
    scale = min(float(size) / (x2 - x1), float(size) / (y2 - y1))
    def sx(x):
        return int(round((x - x1) * scale))
    def sy(y):
        return int(round((y - y1) * scale))
    width, height = sx(x2), sy(y2)
    bitmap = wx.EmptyBitmap(width, height)
    dc = wx.MemoryDC(bitmap)
    font = dc.GetFont()
    font.SetPointSize(14)
    dc.SetFont(font)
    dc.SetBackground(wx.WHITE_BRUSH)
    dc.Clear()
    dc.SetBrush(wx.BLACK_BRUSH)
    dc.SetPen(wx.BLACK_PEN)
    for a, b in model.edges:
        ax, ay = model.nodes[a]
        bx, by = model.nodes[b]
        a = atan2(by - ay, bx - ax)
        ax, ay = ax + cos(a) / 4, ay + sin(a) / 4
        bx, by = bx - cos(a) / 4, by - sin(a) / 4
        dc.DrawLine(sx(ax), sy(ay), sx(bx), sy(by))
        b = a + pi / 2
        cx0, cy0 = bx - cos(a) / 12, by - sin(a) / 12
        cx1, cy1 = cx0 + cos(b) / 24, cy0 + sin(b) / 24
        cx2, cy2 = cx0 - cos(b) / 24, cy0 - sin(b) / 24
        points = [(bx, by), (cx1, cy1), (cx2, cy2), (bx, by)]
        points = [(sx(x), sy(y)) for x, y in points]
        dc.DrawPolygon(points)
    dc.SetBrush(wx.WHITE_BRUSH)
    dc.SetPen(wx.BLACK_PEN)
    for key, (x, y) in model.nodes.items():
        x, y = sx(x), sy(y)
        dc.DrawCircle(x, y, int(scale / 4))
        text = str(key)
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, x - tw / 2, y - th / 2)
    return bitmap

def main():
    edges1 = [
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
    edges2 = [
        (1, 2),
        (1, 5),
        (2, 5),
        (2, 3),
        (3, 4),
        (4, 5),
        (4, 6),
    ]
    edges3 = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    edges4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    edges5 = [(0, 1), (1, 2), (2, 0)]
    edges6 = [(1, 2), (1, 5), (1, 8), (5, 6), (2, 3), (3, 4), (4, 2), (6, 7), (6, 8), (6, 3)]
    model = graph.layout(edges6)
    bitmap = render(model, 800)
    bitmap.SaveFile('output.png', wx.BITMAP_TYPE_PNG)

if __name__ == '__main__':
    main()
