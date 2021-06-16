import wx
import numpy as np
from wxgraph import (DrawObjectRectangle,
                     DrawObjectCircle,
                     DrawObjectPointSet,
                     DrawObjectScaledTextBox,
                     utils,
                     util_bbox)
from .define_gui import *
from .base_state_chart_node import StateChartNode
from .utils_helper import util_section_middle_split


class StateNodeShape(StateChartNode):
    def __init__(self, pos, name='untitled State', evt_desc='Enter:\nExit:\n', in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self.nameText = name
        self.evtDescText = evt_desc
        self.bgColor = '#C7D3D4'
        self.highLightBorderLineColor = '#00FF00'
        self.selectedBorderLineColor = '#FF8000'
        self.defaultBorderLineColor = '#9CC3D5'
        self.nameTextBox = DrawObjectScaledTextBox('', pos, 10, pad_size=5, line_width=0, line_color=self.bgColor,
                                                   color='#603F83',
                                                   weight=wx.FONTWEIGHT_BOLD,
                                                   background_color=self.bgColor)
        self.evtDescTextBox = DrawObjectScaledTextBox('', pos, 8, pad_size=5, line_width=0, line_color=self.bgColor,
                                                      color='#603F83',
                                                      background_color=self.bgColor)
        self._bgRect = DrawObjectRectangle(pos, (1, 1), fill_color=self.bgColor, line_color=self.defaultBorderLineColor)
        self.add_object(self._bgRect)
        self.add_object(self.nameTextBox)
        self.add_object(self.evtDescTextBox)
        self.set_name(name)
        self.set_event_desc_text(evt_desc)

    def set_name(self, text):
        self.nameTextBox.set_text(text)
        self.evtDescTextBox.set_position(
            wx.RealPoint(self.nameTextBox.boundingBox.left, self.nameTextBox.boundingBox.bottom - 5))
        self.calc_bounding_box()
        self._update()

    def set_event_desc_text(self, text):
        self.evtDescTextBox.set_text(text)
        self.calc_bounding_box()
        self._update()

    def set_selected(self, state=True):
        if state:
            self._bgRect.set_line_color(self.selectedBorderLineColor)
        else:
            self._bgRect.set_line_color(self.defaultBorderLineColor)
        self.isSelected = state

    def set_highlighted(self, state=True):
        if state:
            self._bgRect.set_line_color(self.highLightBorderLineColor)
        else:
            self._bgRect.set_line_color(self.defaultBorderLineColor)
        self.isHighlighted = state

    def _update(self):
        _bb_left = self.boundingBox.left
        _bb_top = self.boundingBox.top
        _bb_w = self.boundingBox.width
        _bb_h = self.boundingBox.height
        _rect = wx.Rect(_bb_left, _bb_top, _bb_w, _bb_h).Inflate(2, 2)
        _rect.Offset(0, -1 * self.boundingBox.height)
        self._bgRect.set_shape(_rect.GetTopLeft(), _rect.GetSize())

    def get_connection_points(self):
        # for rectangle shape
        _pts = list()
        _w = self.boundingBox.width
        _h = self.boundingBox.height
        _w_num_sections = util_section_middle_split(_w, self.minConnPtDistance)
        _h_num_sections = util_section_middle_split(_h, self.minConnPtDistance)
        # process h direction conn pts
        for i in range(_h_num_sections):
            _pts.append(((-1, 0), (self.boundingBox.left,
                                   self.boundingBox.center[1] + i * self.minConnPtDistance)))
            if i != 0:
                _pts.append(((-1, 0), (self.boundingBox.left,
                                       self.boundingBox.center[1] - i * self.minConnPtDistance)))
                _pts.append(((1, 0), (self.boundingBox.right,
                                      self.boundingBox.center[1] - i * self.minConnPtDistance)))
            _pts.append(((1, 0), (self.boundingBox.right,
                                  self.boundingBox.center[1] + i * self.minConnPtDistance)))
        for i in range(_w_num_sections):
            _pts.append(((0, 1), (self.boundingBox.center[0] + i * self.minConnPtDistance,
                                  self.boundingBox.top)))
            if i != 0:
                _pts.append(((0, 1), (self.boundingBox.center[0] - i * self.minConnPtDistance,
                                      self.boundingBox.top)))
                _pts.append(
                    ((0, -1), (self.boundingBox.center[0] - i * self.minConnPtDistance,
                               self.boundingBox.bottom)))
            _pts.append(((0, -1), (self.boundingBox.center[0] + i * self.minConnPtDistance,
                                   self.boundingBox.bottom)))
        return _pts

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')


class InitStateNodeShape(StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self._circle = DrawObjectCircle(pos, 16, fill_color='#000000', in_foreground=in_foreground)
        self.add_object(self._circle)

    def get_connection_points(self):
        _bb = self.boundingBox
        _pts = list()
        _pts.append(((0, 1), (_bb.center[0], _bb.top)))
        _pts.append(((0, -1), (_bb.center[0], _bb.bottom)))
        _pts.append(((1, 0), (_bb.right, _bb.center[1])))
        _pts.append(((-1, 0), (_bb.left, _bb.center[1])))
        return _pts

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')


class FinalStateNodeShape(StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self._innerCircle = DrawObjectCircle(pos, 14, fill_color='#000000')
        self._outerCircle = DrawObjectCircle(pos, 22)
        self.add_object(self._innerCircle)
        self.add_object(self._outerCircle)

    def get_connection_points(self):
        _bb = self.boundingBox
        _pts = list()
        _pts.append(((0, 1), (_bb.center[0], _bb.top)))
        _pts.append(((0, -1), (_bb.center[0], _bb.bottom)))
        _pts.append(((1, 0), (_bb.right, _bb.center[1])))
        _pts.append(((-1, 0), (_bb.left, _bb.center[1])))
        return _pts

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')
