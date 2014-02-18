from __future__ import division

from math import atan2, cos, sin, pi
import wx

FONT = 'Helvetica'
BACKGROUND = '#FFFFFF'
NODE_FILL = '#FFEBD3'
NODE_COLOR = '#00283F'
EDGE_COLOR = '#00283F'
TEXT_COLOR = '#00283F'
NODE_WIDTH = 2
EDGE_WIDTH = 2

def render(max_width, max_height, edges, nodes):
    padding = 0.5
    positions = nodes.values()
    x1 = min(x for x, y in positions) - padding
    y1 = min(y for x, y in positions) - padding
    x2 = max(x for x, y in positions) + padding
    y2 = max(y for x, y in positions) + padding
    scale = min(max_width / (x2 - x1), max_height / (y2 - y1))
    def sx(x):
        return (x - x1) * scale
    def sy(y):
        return (y - y1) * scale
    width, height = sx(x2), sy(y2)
    bitmap = wx.EmptyBitmap(width, height)
    dc = wx.MemoryDC(bitmap)
    font = dc.GetFont()
    font.SetFaceName(FONT)
    font.SetPointSize(scale / 8)
    dc.SetFont(font)
    dc.SetTextForeground(TEXT_COLOR)
    dc.SetBackground(wx.Brush(BACKGROUND))
    dc.Clear()
    dc.SetBrush(wx.Brush(EDGE_COLOR))
    dc.SetPen(wx.Pen(EDGE_COLOR, EDGE_WIDTH))
    for a, b in edges:
        ax, ay = nodes[a]
        bx, by = nodes[b]
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
    for key, (x, y) in nodes.items():
        x, y = sx(x), sy(y)
        dc.DrawCircle(x, y, scale / 4)
        text = str(key)
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, x - tw / 2, y - th / 2)
    return bitmap
