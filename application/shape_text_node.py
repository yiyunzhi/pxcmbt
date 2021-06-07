import wx
from wx.adv import PseudoDC
from .shape_rect_node import RectNodeShape


class TextNodeShape(RectNodeShape):
    def __init__(self, text, parent, sh_id=wx.ID_ANY, size=wx.DefaultSize, pos=wx.DefaultPosition):
        RectNodeShape.__init__(self, parent, sh_id, size, pos)
        self.fillBrush = wx.TRANSPARENT_BRUSH
        self.borderPen = wx.BLUE_PEN
        self.text = text
        self.lineHeight = 12
        self.fontSize = 12
        self.textBoldEnabled = True
        self.font = wx.Font(self.fontSize, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.textColor = wx.Colour('#333')
        self.update_size()

    def get_text_size(self):
        _dc = wx.ScreenDC()
        _dc.SetFont(self.font)
        _w, _h = _dc.GetMultiLineTextExtent(self.text)
        return wx.Size(_w, _h)

    def update_size(self):
        if self.textBoldEnabled:
            self.font.SetWeight(wx.BOLD)
        self.size = self.get_text_size()

    def get_bounding_box(self):
        return wx.Rect(self.position + self.relativePosition, self.size)

    def draw(self, pdc: PseudoDC):
        self.update_size()
        _x, _y, _w, _h = self.get_bounding_box()
        pdc.SetId(self._id)
        pdc.SetPen(self.borderPen)
        pdc.SetBrush(wx.Brush(self.fillBrush))
        pdc.DrawRoundedRectangle(_x, _y, _w, _h, self.cornerRadius)
        pdc.SetTextForeground(self.textColor)
        pdc.SetFont(self.font)
        pdc.DrawText(self.text, _x, _y)
        pdc.SetIdBounds(self._id, self.get_bounding_box())