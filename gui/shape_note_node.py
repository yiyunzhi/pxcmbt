import wx
from wx.lib.floatcanvas.FCObjects import ScaledTextBox, Group, Rectangle, Polygon
from .define_gui import *
from .base_state_chart_node import StateChartNode


class NoteNodeShape(Group, StateChartNode):
    def __init__(self, pos, text='Notes...', in_foreground=False, visible=True):
        Group.__init__(self, InForeground=in_foreground, IsVisible=visible)
        StateChartNode.__init__(self)
        self.connectionStyle = EnumShapeConnectionStyle.NONE
        self.text = text
        self.textBoxBgColor = '#abc'
        self.textBox = ScaledTextBox('', pos, 10, PadSize=5, LineWidth=0, LineColor=self.textBoxBgColor,
                                     BackgroundColor=self.textBoxBgColor)
        self._cornerBgPoly = Polygon([pos], FillColor=self.textBoxBgColor)
        self.AddObject(self._cornerBgPoly)
        self.AddObject(self.textBox)
        self._cornerW = 10
        self._cornerH = 10
        self.set_text(text)

    def set_text(self, text):
        self.textBox.SetText(text)
        self._build_corner_style()
        self.CalcBoundingBox()

    def _build_corner_style(self):
        _xy, _wh = self.textBox.GetBoxRect()
        _rect = wx.Rect(_xy, _wh).Inflate(2, 2)
        _rect.Offset(0, -1 * _wh[1])
        _pt1 = _rect.GetTopLeft()
        _pt2 = _rect.GetBottomLeft()
        _pt3 = _rect.GetBottomRight() - wx.Point(self._cornerW, 0)
        _pt4 = _rect.GetBottomRight() + wx.Point(0, self._cornerH)
        _pt5 = _rect.GetTopRight()
        self._cornerBgPoly.SetPoints([_pt1, _pt2, _pt3, _pt4, _pt5])

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')
