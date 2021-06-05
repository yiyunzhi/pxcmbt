import wx
from wx.adv import PseudoDC
from .shape_node import BaseNodeShape
from gui.define_gui import EnumShapeConnectionStyle


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

    def get_center(self):
        _rect = self.get_bounding_box()
        return wx.Point(_rect.GetLeft() + _rect.GetWidth() / 2, _rect.GetTop() + _rect.GetHeight() / 2)

    def contains(self, pt):
        _rect = self.get_bounding_box()
        return _rect.Contains(pt)

    def get_bounding_box(self):
        return wx.Rect(self.position, self.size)

    def draw(self, pdc: PseudoDC):
        _x, _y, _w, _h = self.get_bounding_box()
        pdc.SetId(self._id)
        pdc.SetPen(self.borderPen)
        pdc.SetBrush(wx.Brush(self.fillBrush))
        pdc.DrawRoundedRectangle(_x, _y, _w, _h, self.cornerRadius)
        pdc.SetIdBounds(self._id, self.get_bounding_box())


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


class StateNodeShape(RectNodeShape):
    def __init__(self, parent, sh_id=wx.ID_ANY, title='TitleState', size=wx.DefaultSize, pos=wx.DefaultPosition):
        RectNodeShape.__init__(self, parent, sh_id, size, pos)
        # todo: has style auto round corner
        self.connectionStyle = EnumShapeConnectionStyle.ANYWHERE
        self.borderPen = wx.Pen(wx.BLACK, 1)
        self.fillBrush = wx.Brush(wx.Colour(170, 217, 233))
        self.hoverBorderPen = wx.Pen(wx.Colour(150, 197, 213))
        self.hoverFillBrush = wx.Brush(wx.Colour(170, 217, 233))
        self.cornerRadius = 12
        self.titleShape = TextNodeShape(title, self, wx.ID_ANY)
        self.add_child(self.titleShape)

    def get_bounding_box(self):
        _rect = wx.Rect(self.position + self.relativePosition, self.size)
        for nid, shape in self.childShapes.items():
            _rect = _rect.Union(shape.get_bounding_box())
        return _rect.Inflate(8, 0)

    def align_text_to_center(self):
        # todo: better is, use Enum define the align center, left,right to determine the relative position
        _text_size = self.titleShape.size
        _text_center = wx.Point(self.titleShape.position.x + _text_size.GetWidth() / 2,
                                self.titleShape.position.y + _text_size.GetHeight() / 2)
        self.titleShape.set_relative_position(self.get_center() - _text_center)

    def _recalculate_radius(self):
        self.cornerRadius = int(self.size.GetHeight() / 2)

    def draw(self, pdc):
        self._recalculate_radius()
        self.align_text_to_center()
        _x, _y, _w, _h = self.get_bounding_box()
        pdc.SetId(self._id)
        if self.isMouseOvered:
            print('-->mouse overed')
            _pen = self.hoverBorderPen
            _fillBrush = self.hoverFillBrush
        else:
            _pen = self.borderPen
            _fillBrush = self.fillBrush
        pdc.SetPen(_pen)
        pdc.SetBrush(_fillBrush)
        pdc.DrawRoundedRectangle(_x, _y, _w, _h, self.cornerRadius)
        pdc.SetIdBounds(self._id, self.get_bounding_box())
        for nid, child in self.childShapes.items():
            child.draw(pdc)
