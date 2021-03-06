import wx.propgrid as wxpg
from wxgraph import (DrawObjectRectangle,
                     DrawObjectCircle,
                     DrawObjectScaledTextBox)
from .define_gui import *
from .base_state_chart_node import StateChartNode
from application.utils_helper import util_section_middle_split
from application.define import EnumItemRole


class StateNodeShape(StateChartNode):
    def __init__(self, pos, name='untitled State', in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self.position = pos
        self.nameText = name
        self.bgColor = '#C7D3D4'
        self.nameTextBox = DrawObjectScaledTextBox('', pos, 10, width=120, pad_size=5, line_width=0,
                                                   line_color=self.bgColor,
                                                   color='#603F83',
                                                   weight=wx.FONTWEIGHT_BOLD,
                                                   background_color=self.bgColor)
        self.evtDescTextBox = DrawObjectScaledTextBox('', pos, 7, width=120, pad_size=5, line_width=0,
                                                      line_color=self.bgColor,
                                                      color='#603F83',
                                                      background_color=self.bgColor)
        self._bgRect = DrawObjectRectangle(pos, (126, 1), fill_color=self.bgColor,
                                           line_color=self.defaultBorderLineColor)
        self.add_object(self._bgRect)
        self.add_object(self.nameTextBox)
        self.add_object(self.evtDescTextBox)
        self.set_name(name)
        self.update_event_desc_text()

    def get_properties(self, pg_parent):
        _pg_main = wxpg.PropertyGridManager(pg_parent, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED)
        _pg_uuid = wxpg.StringProperty("uuid", 'uuid', value=self.uuid)
        _pg_main.SetPropertyReadOnly(_pg_uuid)
        _pg_main.Append(_pg_uuid)

        _pg_role = wxpg.StringProperty("role", 'role', value=EnumItemRole(self.role).name)
        _pg_main.SetPropertyReadOnly(_pg_role)
        _pg_main.Append(_pg_role)

        _pg_position = wxpg.StringProperty("position", 'position',
                                           value='(%s,%s)' % (self.position[0], self.position[1]))
        _pg_main.SetPropertyReadOnly(_pg_position)
        _pg_main.Append(_pg_position)

        _pg_name = wxpg.StringProperty("name", 'name',
                                       value=self.nameText)
        _pg_main.SetPropertyReadOnly(_pg_name)
        _pg_main.Append(_pg_name)

        return _pg_main

    def serialize(self):
        _d = dict()
        _d.update({'class': self.__class__.__name__})
        _d.update({'uuid': self.uuid})
        _d.update({'role': self.role})
        _d.update({'nameText': self.nameText})
        _d.update({'isVisible': self.isVisible})
        _d.update({'bbox': self._bgRect.boundingBox})
        _d.update({'position': tuple(self.position)})
        _d.update({'connectionStyle': self.connectionStyle})
        _d.update({'exitEventModel': self.exitEventModel})
        _d.update({'enterEventModel': self.enterEventModel})
        return _d

    def set_name(self, name):
        self.nameText = name
        self.nameTextBox.set_text(name)
        self.evtDescTextBox.set_position(
            wx.RealPoint(self.nameTextBox.boundingBox.left, self.nameTextBox.boundingBox.bottom - 5))
        self.update_bg()

    def update_event_desc_text(self):
        _enter = self.enterEventModel.get_event_names()
        _exit = self.exitEventModel.get_event_names()
        _text = 'Enter: (%s)' % len(_enter) + '\n' + 'Exit: (%s)' % len(_exit)
        self.evtDescTextBox.set_text(_text)
        self.update_bg()

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

    def update_bg(self):
        self.calc_bounding_box()
        _bb_left = self.nameTextBox.boundingBox.left
        _bb_top = self.nameTextBox.boundingBox.top
        _bb_w = self.nameTextBox.boundingBox.width
        _bb_h = self.nameTextBox.boundingBox.height+self.evtDescTextBox.boundingBox.height+5
        _rect = wx.Rect(_bb_left, _bb_top, _bb_w, _bb_h).Inflate(2, 2)
        _rect.Offset(0, -1 * _bb_h)
        _size = _rect.GetSize()
        self._bgRect.set_shape(_rect.GetTopLeft(), (126, _size.GetHeight()))

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
        #print('state left down')
        pass

    def on_enter(self):
        #print('state on_enter')
        pass

    def on_leave(self):
        #print('state on_leave')
        pass

    def on_left_up(self):
        #print('state on left up')
        pass


class InitStateNodeShape(StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self.position = pos
        self.nameText='INIT'
        self._circle = DrawObjectCircle(pos, 16,
                                        line_color=self.defaultBorderLineColor,
                                        fill_color=self.defaultBorderLineColor,
                                        in_foreground=in_foreground)
        self.add_object(self._circle)

    def serialize(self):
        _d = dict()
        _d.update({'class': self.__class__.__name__})
        _d.update({'nameText': self.nameText})
        _d.update({'uuid': self.uuid})
        _d.update({'role': self.role})
        _d.update({'isVisible': self.isVisible})
        _d.update({'position': tuple(self.position)})
        _d.update({'connectionStyle': self.connectionStyle})
        return _d

    def get_properties(self, pg_parent):
        _pg_main = wxpg.PropertyGridManager(pg_parent, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED)
        _pg_uuid = wxpg.StringProperty("uuid", 'uuid', value=self.uuid)
        _pg_main.SetPropertyReadOnly(_pg_uuid)
        _pg_main.Append(_pg_uuid)

        _pg_role = wxpg.StringProperty("role", 'role', value=EnumItemRole(self.role).name)
        _pg_main.SetPropertyReadOnly(_pg_role)
        _pg_main.Append(_pg_role)

        _pg_name = wxpg.StringProperty("name", 'name', value=self.nameText)
        _pg_main.SetPropertyReadOnly(_pg_name)
        _pg_main.Append(_pg_name)

        _pg_position = wxpg.StringProperty("position", 'position',
                                           value='(%s,%s)' % (self.position[0], self.position[1]))
        _pg_main.SetPropertyReadOnly(_pg_position)
        _pg_main.Append(_pg_position)

        return _pg_main

    def get_connection_points(self):
        _bb = self.boundingBox
        _pts = list()
        _pts.append(((0, 1), (_bb.center[0]+3, _bb.top)))
        _pts.append(((0, -1), (_bb.center[0]+3, _bb.bottom)))
        _pts.append(((1, 0), (_bb.right+1, _bb.center[1])))
        _pts.append(((-1, 0), (_bb.left+3, _bb.center[1])))
        return _pts

    def set_selected(self, state=True):
        if state:
            self._circle.set_line_color(self.selectedBorderLineColor)
            self._circle.set_fill_color(self.selectedBorderLineColor)
        else:
            self._circle.set_line_color(self.defaultBorderLineColor)
            self._circle.set_fill_color(self.defaultBorderLineColor)
        self.isSelected = state

    def on_left_down(self):
        #print('state left down')
        pass

    def on_enter(self):
        #print('state on_enter')
        pass

    def on_leave(self):
        #print('state on_leave')
        pass

    def on_left_up(self):
        #print('state on left up')
        pass


class FinalStateNodeShape(StateChartNode):
    def __init__(self, pos, in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self.position = pos
        self.nameText = 'FINAL'
        self._innerCircle = DrawObjectCircle(pos, 14, fill_color='#000000')
        self._outerCircle = DrawObjectCircle(pos, 22, line_color=self.defaultBorderLineColor)
        self.add_object(self._innerCircle)
        self.add_object(self._outerCircle)

    def serialize(self):
        _d = dict()
        _d.update({'class': self.__class__.__name__})
        _d.update({'nameText': self.nameText})
        _d.update({'uuid': self.uuid})
        _d.update({'role': self.role})
        _d.update({'isVisible': self.isVisible})
        _d.update({'position': tuple(self.position)})
        _d.update({'connectionStyle': self.connectionStyle})
        return _d

    def get_properties(self, pg_parent):
        _pg_main = wxpg.PropertyGridManager(pg_parent, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED)
        _pg_uuid = wxpg.StringProperty("uuid", 'uuid', value=self.uuid)
        _pg_main.SetPropertyReadOnly(_pg_uuid)
        _pg_main.Append(_pg_uuid)

        _pg_role = wxpg.StringProperty("role", 'role', value=EnumItemRole(self.role).name)
        _pg_main.SetPropertyReadOnly(_pg_role)
        _pg_main.Append(_pg_role)

        _pg_name = wxpg.StringProperty("name", 'name', value=self.nameText)
        _pg_main.SetPropertyReadOnly(_pg_name)
        _pg_main.Append(_pg_name)

        _pg_position = wxpg.StringProperty("position", 'position',
                                           value='(%s,%s)' % (self.position[0], self.position[1]))
        _pg_main.SetPropertyReadOnly(_pg_position)
        _pg_main.Append(_pg_position)

        return _pg_main

    def get_connection_points(self):
        _bb = self.boundingBox
        _pts = list()
        _pts.append(((0, 1), (_bb.center[0]+3, _bb.top)))
        _pts.append(((0, -1), (_bb.center[0]+3, _bb.bottom)))
        _pts.append(((1, 0), (_bb.right+1, _bb.center[1])))
        _pts.append(((-1, 0), (_bb.left+3, _bb.center[1])))
        return _pts

    def set_selected(self, state=True):
        if state:
            self._outerCircle.set_line_color(self.selectedBorderLineColor)
        else:
            self._outerCircle.set_line_color(self.defaultBorderLineColor)
        self.isSelected = state

    def on_left_down(self):
        #print('state left down')
        pass

    def on_enter(self):
        #print('state on_enter')
        pass

    def on_leave(self):
        #print('state on_leave')
        pass

    def on_left_up(self):
        #print('state on left up')
        pass
