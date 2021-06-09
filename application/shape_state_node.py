import wx
from wx.adv import PseudoDC
from .shape_rect_node import RectNodeShape
from .shape_text_node import TextNodeShape
from .shape_circle_node import CircleNodeShape
from __gui_v1.define_gui import EnumShapeConnectionStyle


class StateNodeShape(RectNodeShape):
    def __init__(self, parent, sh_id=wx.ID_ANY, title='TitleState', size=wx.DefaultSize, pos=wx.DefaultPosition):
        RectNodeShape.__init__(self, parent, sh_id, size, pos)
        # todo: has style auto round corner
        # todo: in function contains implements, if round corner contains the given point
        self.connectionStyle = EnumShapeConnectionStyle.ANYWHERE
        self.borderPen = wx.Pen(wx.BLACK, 1)
        self.fillBrush = wx.Brush(wx.Colour(170, 217, 233))
        self.hoverBorderPen = wx.Pen(wx.Colour(150, 197, 213))
        self.hoverFillBrush = wx.Brush(wx.Colour(170, 217, 233))
        self.cornerRadius = 12
        self.titleShape = TextNodeShape(title, self, wx.ID_ANY)
        self.add_child(self.titleShape)

    def scale(self, x, y, include_children=True):
        pass

    def get_bounding_box(self):
        _rect = wx.Rect(self.position + self.relativePosition, self.size)
        for nid, shape in self.childShapes.items():
            _rect = _rect.Union(shape.get_bounding_box())
        return _rect.Inflate(self.borderPen.GetWidth(), self.borderPen.GetWidth())

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
        pdc.ClearId(self._id)
        pdc.SetId(self._id)
        if self.isMouseOvered:
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


class StateInitNodeShape(CircleNodeShape):
    def __init__(self, parent, sh_id=wx.ID_ANY, size=wx.DefaultSize, pos=wx.DefaultPosition):
        CircleNodeShape.__init__(self, parent, sh_id, size, pos)
        self.fillBrush = wx.BLACK_BRUSH


class StateFinalNodeShape(CircleNodeShape):
    def __init__(self, parent, sh_id=wx.ID_ANY, size=wx.DefaultSize, pos=wx.DefaultPosition):
        CircleNodeShape.__init__(self, parent, sh_id, size, pos)
        self.fillBrush = wx.BLACK_BRUSH
        self.innerRadius = self.radius - 4

    def draw(self, pdc: PseudoDC):
        _x, _y, _w, _h = self.get_bounding_box()
        pdc.SetId(self._id)
        pdc.SetPen(self.borderPen)
        pdc.SetBrush(wx.TRANSPARENT_BRUSH)
        pdc.DrawCircle(_x + self.radius, _y + self.radius, self.radius)
        pdc.SetBrush(wx.Brush(self.fillBrush))
        pdc.DrawCircle(_x + self.radius, _y + self.radius, self.innerRadius)
        pdc.SetIdBounds(self._id, self.get_bounding_box())
