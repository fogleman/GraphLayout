import graph
import wx

def render(model, size):
    app = wx.App(None)
    x1 = min(x for x, y in model.nodes.values())
    y1 = min(y for x, y in model.nodes.values())
    x2 = max(x for x, y in model.nodes.values())
    y2 = max(y for x, y in model.nodes.values())
    x1, y1 = x1 - 1, y1 - 1
    x2, y2 = x2 + 1, y2 + 1
    scale = min(float(size) / (x2 - x1), float(size) / (y2 - y1))
    width, height = int((x2 - x1) * scale), int((y2 - y1) * scale)
    bitmap = wx.EmptyBitmap(width, height)
    dc = wx.MemoryDC(bitmap)
    dc.SetBackground(wx.WHITE_BRUSH)
    dc.Clear()
    dc.SetBrush(wx.WHITE_BRUSH)
    dc.SetPen(wx.BLACK_PEN)
    for a, b in model.edges:
        ax, ay = model.nodes[a]
        ax = int((ax - x1) * scale)
        ay = int((ay - y1) * scale)
        bx, by = model.nodes[b]
        bx = int((bx - x1) * scale)
        by = int((by - y1) * scale)
        dc.DrawLine(ax, ay, bx, by)
    for key, (x, y) in model.nodes.items():
        x = int((x - x1) * scale)
        y = int((y - y1) * scale)
        dc.DrawCircle(x, y, int(scale / 4))
        text = str(key)
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, x - tw / 2, y - th / 2)
    return bitmap

def main():
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
    model.energy(True) # prints debug output
    bitmap = render(model, 800)
    bitmap.SaveFile('output.png', wx.BITMAP_TYPE_PNG)

if __name__ == '__main__':
    main()
