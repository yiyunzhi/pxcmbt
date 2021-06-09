import wx
from wx.adv import PseudoDC
from .shape_node import BaseNodeShape


class CircleNodeShape(BaseNodeShape):
    def __init__(self, parent, sh_id=wx.ID_ANY, size=wx.DefaultSize, pos=wx.DefaultPosition):
        BaseNodeShape.__init__(self, parent, sh_id)
        self.borderPen = wx.Pen(wx.BLACK, 1)
        self.fillBrush = wx.Brush(wx.LIGHT_GREY)
        self.size = size
        self.position = pos
        self.radius = min([size.x/2, size.y/2])

    def get_center(self):
        _rect = self.get_bounding_box()
        return wx.Point(_rect.GetLeft() + _rect.GetWidth() / 2, _rect.GetTop() + _rect.GetHeight() / 2)

    def contains(self, pt):
        _rect = self.get_bounding_box()
        return _rect.Contains(pt)

    def get_bounding_box(self):
        return wx.Rect(self.position, self.size).Inflate(self.borderPen.GetWidth(),self.borderPen.GetWidth())

    def draw(self, pdc: PseudoDC):
        _x, _y, _w, _h = self.get_bounding_box()
        pdc.SetId(self._id)
        pdc.SetPen(self.borderPen)
        pdc.SetBrush(wx.Brush(self.fillBrush))
        pdc.DrawCircle(_x+self.radius, _y+self.radius,self.radius)
        pdc.SetIdBounds(self._id, self.get_bounding_box())
