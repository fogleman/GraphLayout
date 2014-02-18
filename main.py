from math import atan2, cos, sin, pi
import layout
import threading
import wx

BACKGROUND = '#FFFFFF'
NODE_FILL = '#FFEBD3'
NODE_COLOR = '#00283F'
EDGE_COLOR = '#00283F'
TEXT_COLOR = '#00283F'
NODE_WIDTH = 2
EDGE_WIDTH = 2

def render(model, size):
    padding = 0.5
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
    font.SetFaceName('Helvetica')
    font.SetPointSize(int(scale / 8))
    dc.SetFont(font)
    dc.SetTextForeground(TEXT_COLOR)
    dc.SetBackground(wx.Brush(BACKGROUND))
    dc.Clear()
    dc.SetBrush(wx.Brush(EDGE_COLOR))
    dc.SetPen(wx.Pen(EDGE_COLOR, EDGE_WIDTH))
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
    dc.SetBrush(wx.Brush(NODE_FILL))
    dc.SetPen(wx.Pen(NODE_COLOR, NODE_WIDTH))
    for key, (x, y) in model.nodes.items():
        x, y = sx(x), sy(y)
        dc.DrawCircle(x, y, int(scale / 4))
        text = str(key)
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, x - tw / 2, y - th / 2)
    return bitmap

class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.model = None
        self.bitmap = None
    def update(self):
        if self.model is None:
            return
        cw, ch = self.GetClientSize()
        size = min(cw, ch)
        bitmap = render(self.model, size)
        self.set_bitmap(bitmap)
    def set_model(self, model):
        self.model = model
        self.update()
    def set_bitmap(self, bitmap):
        self.bitmap = bitmap
        self.Refresh()
        self.Update()
    def on_size(self, event):
        event.Skip()
        self.update()
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(BACKGROUND))
        dc.Clear()
        if self.bitmap is None:
            return
        cw, ch = self.GetClientSize()
        bw, bh = self.bitmap.GetSize()
        x = cw / 2 - bw / 2
        y = ch / 2 - bh / 2
        dc.DrawBitmap(self.bitmap, x, y)

def main():
    edges1 = [(5, 11), (11, 10), (11, 2), (3, 10), (3, 8), (8, 9), (11, 9), (7, 8), (7, 11)]
    edges2 = [(1, 2), (1, 5), (2, 5), (2, 3), (3, 4), (4, 5), (4, 6)]
    edges3 = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    edges4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    edges5 = [(0, 1), (1, 2), (2, 0)]
    edges6 = [(1, 2), (1, 5), (1, 8), (5, 6), (2, 3), (3, 4), (4, 2), (6, 7), (6, 8), (6, 3)]
    edges7 = [(1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 6), (4, 3), (4, 6), (4, 7), (5, 4), (5, 7), (7, 6)]
    edges8 = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 4), (2, 5), (3, 6)]
    app = wx.App(None)
    frame = wx.Frame(None)
    panel = Panel(frame)
    frame.SetTitle('GraphLayout')
    frame.SetClientSize((600, 600))
    frame.Center()
    frame.Show()
    def listener(state, energy):
        wx.CallAfter(panel.set_model, state)
    def run():
        model = layout.layout(edges1, 100000, listener)
        wx.CallAfter(panel.set_model, model)
    thread = threading.Thread(target=run)
    thread.start()
    app.MainLoop()

if __name__ == '__main__':
    main()
