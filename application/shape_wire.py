import wx
from application.define import *
from .shape_node import BaseNodeShape


class WireNodeShape(BaseNodeShape):
    def __init__(self, parent, sh_id, src_pt=wx.DefaultPosition, dst_pt=wx.DefaultPosition):
        BaseNodeShape.__init__(self, parent, sh_id)
        self.borderPen = wx.Pen(wx.BLACK, 1)
        self.srcPoint = src_pt
        self.dstPoint = dst_pt

    def contains(self, pt):
        return False

    def get_bounding_box(self):
        _min_x = min(self.srcPoint[0], self.dstPoint[0])
        _min_y = min(self.srcPoint[1], self.dstPoint[1])
        _size = self.dstPoint - self.srcPoint
        _rect = wx.Rect(_min_x - 10, _min_y, abs(_size[0]) + 20, abs(_size[1]))
        return _rect.Inflate(self.borderPen.GetWidth(), self.borderPen.GetWidth())

    def draw(self, pdc):
        pdc.SetId(self._id)
        # for source / destination drawing direction.
        _sign = 1
        _pts = list()
        _pts.append(self.srcPoint)
        _pts.append(self.srcPoint + wx.Point(10 * _sign, 0))
        _pts.append(self.dstPoint - wx.Point(10 * _sign, 0))
        _pts.append(self.dstPoint)
        pdc.SetPen(self.borderPen)
        pdc.DrawSpline(_pts)
        pdc.SetIdBounds(self._id, self.get_bounding_box())
