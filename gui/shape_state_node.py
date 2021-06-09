import wx
from wx.lib.floatcanvas import FloatCanvas
from wx.lib.floatcanvas.FCObjects import ScaledTextBox, Group, Rectangle, Polygon, Circle
from .define_gui import *
from .base_state_chart_node import StateChartNode


class StateNodeShape(Group, StateChartNode):
    def __init__(self, pos, name='untitled State', evt_desc='Enter:\nExit:\n', in_foreground=False, visible=True):
        Group.__init__(self, InForeground=in_foreground, IsVisible=visible)
        StateChartNode.__init__(self)
        self.nameText = name
        self.evtDescText = evt_desc
        self.bgColor = '#C7D3D4'
        self.nameTextBox = ScaledTextBox('', pos, 10, PadSize=5, LineWidth=0, LineColor=self.bgColor,
                                         Color='#603F83',
                                         Weight=wx.FONTWEIGHT_BOLD,
                                         BackgroundColor=self.bgColor)
        self.evtDescTextBox = ScaledTextBox('', pos, 8, PadSize=5, LineWidth=0, LineColor=self.bgColor,
                                            Color='#603F83',
                                            BackgroundColor=self.bgColor)
        self._bgRect = Rectangle(pos, (1, 1), FillColor=self.bgColor, LineColor='#9CC3D5')
        self.AddObject(self._bgRect)
        self.AddObject(self.nameTextBox)
        self.AddObject(self.evtDescTextBox)
        self.set_name(name)
        self.set_event_desc_text(evt_desc)

    def set_name(self, text):
        self.nameTextBox.SetText(text)
        # _xy, _wh = self.nameTextBox.GetBoxRect()
        # self.evtDescTextBox.SetLineWidth()
        # self.evtDescTextBox.LineWidth
        self.evtDescTextBox.SetPoint(
            wx.RealPoint(self.nameTextBox.BoundingBox.Left, self.nameTextBox.BoundingBox.Bottom - 5))
        self.CalcBoundingBox()
        self._update()

    def set_event_desc_text(self, text):
        self.evtDescTextBox.SetText(text)
        self.CalcBoundingBox()
        self._update()

    def _update(self):
        _bb_left = self.BoundingBox.Left
        _bb_top = self.BoundingBox.Top
        _bb_w = self.BoundingBox.Width
        _bb_h = self.BoundingBox.Height
        _rect = wx.Rect(_bb_left, _bb_top, _bb_w, _bb_h).Inflate(2, 2)
        _rect.Offset(0, -1 * self.BoundingBox.Height)
        self._bgRect.SetShape(_rect.GetTopLeft(), _rect.GetSize())

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')


class InitStateNodeShape(Circle, StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        Circle.__init__(self, pos, 10, FillColor='#000000', InForeground=in_foreground)
        StateChartNode.__init__(self)

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')


class FinalStateNodeShape(Group, StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        Group.__init__(self, InForeground=in_foreground, IsVisible=visible)
        StateChartNode.__init__(self)
        self._innerCircle = Circle(pos, 8, FillColor='#000000')
        self._outerCircle = Circle(pos, 16)
        self.AddObject(self._innerCircle)
        self.AddObject(self._outerCircle)

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')
