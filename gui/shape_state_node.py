import wx
from wxgraph import DrawObjectRectangle, DrawObjectCircle, DrawObjectGroup, DrawObjectScaledTextBox
from .define_gui import *
from .base_state_chart_node import StateChartNode


class StateNodeShape(DrawObjectGroup, StateChartNode):
    def __init__(self, pos, name='untitled State', evt_desc='Enter:\nExit:\n', in_foreground=False, visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=visible)
        StateChartNode.__init__(self)
        self.nameText = name
        self.evtDescText = evt_desc
        self.bgColor = '#C7D3D4'
        self.nameTextBox = DrawObjectScaledTextBox('', pos, 10, pad_size=5, line_width=0, line_color=self.bgColor,
                                                   color='#603F83',
                                                   weight=wx.FONTWEIGHT_BOLD,
                                                   background_color=self.bgColor)
        self.evtDescTextBox = DrawObjectScaledTextBox('', pos, 8, pad_size=5, line_width=0, line_color=self.bgColor,
                                                      color='#603F83',
                                                      background_color=self.bgColor)
        self._bgRect = DrawObjectRectangle(pos, (1, 1), fill_color=self.bgColor, line_color='#9CC3D5')
        self.add_object(self._bgRect)
        self.add_object(self.nameTextBox)
        self.add_object(self.evtDescTextBox)
        self.set_name(name)
        self.set_event_desc_text(evt_desc)

    def set_name(self, text):
        self.nameTextBox.set_text(text)
        # _xy, _wh = self.nameTextBox.GetBoxRect()
        # self.evtDescTextBox.SetLineWidth()
        # self.evtDescTextBox.LineWidth
        self.evtDescTextBox.set_position(
            wx.RealPoint(self.nameTextBox.boundingBox.left, self.nameTextBox.boundingBox.bottom - 5))
        self.calc_bounding_box()
        self._update()

    def set_event_desc_text(self, text):
        self.evtDescTextBox.set_text(text)
        self.calc_bounding_box()
        self._update()

    def _update(self):
        _bb_left = self.boundingBox.left
        _bb_top = self.boundingBox.top
        _bb_w = self.boundingBox.width
        _bb_h = self.boundingBox.height
        _rect = wx.Rect(_bb_left, _bb_top, _bb_w, _bb_h).Inflate(2, 2)
        _rect.Offset(0, -1 * self.boundingBox.height)
        self._bgRect.set_shape(_rect.GetTopLeft(), _rect.GetSize())

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')


class InitStateNodeShape(DrawObjectCircle, StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        DrawObjectCircle.__init__(self, pos, 10, fill_color='#000000', in_foreground=in_foreground)
        StateChartNode.__init__(self)

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')


class FinalStateNodeShape(DrawObjectGroup, StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=visible)
        StateChartNode.__init__(self)
        self._innerCircle = DrawObjectCircle(pos, 8, fill_color='#000000')
        self._outerCircle = DrawObjectCircle(pos, 16)
        self.add_object(self._innerCircle)
        self.add_object(self._outerCircle)

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')
