import layout
import render
import wx

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
        bitmap = render.render(cw, ch, *self.model)
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
        dc.SetBackground(wx.Brush(render.BACKGROUND))
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
    edges9 = [(1, 3), (3, 2), (2, 1), (3, 5), (4, 1), (4, 2), (4, 12), (4, 13), (5, 6), (5, 8), (6, 7), (6, 8), (6, 10), (7, 10), (8, 9), (8, 10), (9, 5), (9, 11), (10, 9), (10, 11), (10, 14), (11, 12), (11, 14), (12, 13), (13, 11), (13, 15), (14, 13), (15, 14)]
    edges10 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    edges = edges1
    nodes = layout.layout(edges)
    app = wx.App(None)
    frame = wx.Frame(None)
    panel = Panel(frame)
    frame.SetTitle('GraphLayout')
    frame.SetClientSize((600, 600))
    frame.Center()
    frame.Show()
    panel.set_model((edges, nodes))
    app.MainLoop()

if __name__ == '__main__':
    main()
