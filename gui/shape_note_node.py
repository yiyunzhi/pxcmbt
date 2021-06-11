import wx
from wxgraph import DrawObjectPolygon, DrawObjectGroup, DrawObjectScaledTextBox
from .define_gui import *
from .base_state_chart_node import StateChartNode


class NoteNodeShape(DrawObjectGroup, StateChartNode):
    def __init__(self, pos, text='Notes...', in_foreground=False, visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=visible)
        StateChartNode.__init__(self)
        self.connectionStyle = EnumShapeConnectionStyle.NONE
        self.text = text
        self.textBoxBgColor = '#abc'
        self.textBox = DrawObjectScaledTextBox('', pos, 10, pad_size=5, line_width=0, line_color=self.textBoxBgColor,
                                               background_color=self.textBoxBgColor)
        self._cornerBgPoly = DrawObjectPolygon([pos], fill_color=self.textBoxBgColor)
        self.add_object(self._cornerBgPoly)
        self.add_object(self.textBox)
        self._cornerW = 10
        self._cornerH = 10
        self.set_text(text)

    def set_text(self, text):
        self.textBox.set_text(text)
        self._build_corner_style()
        self.calc_bounding_box()

    def _build_corner_style(self):
        _xy, _wh = self.textBox.get_box_rect()
        _rect = wx.Rect(_xy, _wh).Inflate(2, 2)
        _rect.Offset(0, -1 * _wh[1])
        _pt1 = _rect.GetTopLeft()
        _pt2 = _rect.GetBottomLeft()
        _pt3 = _rect.GetBottomRight() - wx.Point(self._cornerW, 0)
        _pt4 = _rect.GetBottomRight() + wx.Point(0, self._cornerH)
        _pt5 = _rect.GetTopRight()
        self._cornerBgPoly.set_points([_pt1, _pt2, _pt3, _pt4, _pt5])

    def on_left_down(self,*args):
        print('state left down',*args)

    def on_enter(self,*args):
        print('state on_enter',*args)

    def on_leave(self,*args):
        print('state on_leave',*args)

    def on_left_up(self,*args):
        print('state on left up',*args)
