import wx
from wx.adv import PseudoDC
from .shape_node import BaseNodeShape


class RectNodeShape(BaseNodeShape):
    def __init__(self, parent, sh_id=wx.ID_ANY, size=wx.DefaultSize, pos=wx.DefaultPosition):
        BaseNodeShape.__init__(self, parent, sh_id)
        self.borderPen = wx.Pen(wx.BLACK, 1)
        self.fillBrush = wx.Brush(wx.LIGHT_GREY)
        self.size = size
        self.position = pos
        self.cornerRadius = 0

    def set_corner_radius(self, radius):
        self.cornerRadius = radius

    def get_bounding_box(self):
        return wx.Rect(self.position, self.size)

    def draw(self, pdc: PseudoDC):
        _x, _y, _w, _h = self.get_bounding_box()
        pdc.SetId(self._id)
        pdc.SetPen(self.borderPen)
        pdc.SetBrush(wx.Brush(self.fillBrush))
        pdc.DrawRoundedRectangle(_x, _y, _w, _h, self.cornerRadius)
        pdc.SetIdBounds(self._id, self.get_bounding_box())


class StateNodeShape(BaseNodeShape):
    def __init__(self, parent):
        BaseNodeShape.__init__(self, parent, sh_id=wx.ID_ANY)
        self.roundCornerRadius = 10

    def get_bounding_box(self):
        return wx.Rect()

    def draw(self, dc):
        x, y, w, h = self.get_bounding_box()

        dc.SetId(self._id)

        dc.SetPen(self.borderPen)
        dc.SetBrush(wx.Brush(self.fillBrush))
        dc.DrawRoundedRectangle(x, y, w, h, self.roundCornerRadius)

        # newFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        # newFont.SetWeight(wx.BOLD)
        # dc.SetFont(newFont)
        #
        # dc.DrawText(self._text, x + TITLE_INSET_X, y + TITLE_INSET_Y)
        #
        # # Draw ins / outs.
        # for port in self._ports:
        #     port.Draw(dc)

        # dc.SetIdBounds(self._id, self._rect)
