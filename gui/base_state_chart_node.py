import math
from collections import OrderedDict
import numpy as np
from .define_gui import *
from wxgraph import DrawObjectPointSet
from wxgraph import util_bbox, DrawObjectGroup, utils
from application.define import EnumItemRole


class Serializable:
    def __init__(self):
        pass

    def get_properties(self):
        pass

    def set_property(self, prop_name, prop_val):
        pass

    def get_property(self, prop_name):
        pass

    def serialize(self):
        pass

    def deserialize(self, data):
        pass


class NodeEvtModel:
    def __init__(self):
        self.events = list()

    def get_event_names(self):
        return [x[0] for x in self.events]

    def clear(self):
        self.events.clear()

    def update(self, event_name, event_data):
        self.events.append((event_name, event_data))


class StateChartNode(Serializable, DrawObjectGroup):
    CONN_PT_SHAPE_DIAMETER = 4

    def __init__(self, in_foreground=False, is_visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=is_visible)
        Serializable.__init__(self)
        self.uuid = None
        self.role = EnumItemRole.ITEM_STATE
        self.enterEventModel = NodeEvtModel()
        self.exitEventModel = NodeEvtModel()
        self.highLightBorderLineColor = '#00FF00'
        self.selectedBorderLineColor = '#FF8000'
        self.defaultBorderLineColor = '#9CC3D5'
        self.shapeStyle = EnumShapeStyle.STYLE_DEFAULT
        self.connectionStyle = EnumShapeConnectionStyle.ANYWHERE
        self._connectionPtShape = DrawObjectPointSet([(0, 0)], diameter=self.CONN_PT_SHAPE_DIAMETER,
                                                     color='transparent')
        self._connectionPtShape.set_pen('#0bc', "Solid", 0.5)
        self.isSelected = False
        self.isHighlighted = False
        self.minConnPtDistance = 30
        self.inWires = list()
        self.outWires = list()

    def get_properties(self, *args):
        pass

    def add_in_wire(self, wire):
        self.inWires.append(wire)

    def add_out_wire(self, wire):
        self.outWires.append(wire)

    def remove_in_wire(self, wire=None):
        if wire is None:
            self.inWires.clear()
        elif wire in self.inWires:
            self.inWires.remove(wire)

    def remove_out_wire(self, wire=None):
        if wire is None:
            self.outWires.clear()
        elif wire in self.outWires:
            self.outWires.remove(wire)

    def has_style(self, style):
        return (self.shapeStyle & style) != 0

    def add_style(self, style):
        self.shapeStyle |= style

    def get_connection_style(self):
        return self.connectionStyle

    def set_connection_style(self, style: EnumShapeConnectionStyle):
        self.connectionStyle = style

    def set_highlighted(self, state):
        pass

    def set_selected(self, state):
        pass

    def get_connection_points_shape(self):
        _conn_pts = self.get_connection_points()
        if _conn_pts is None:
            return None
        _lst_conn_pts = [x[1] for x in _conn_pts]
        self._connectionPtShape.set_points(_lst_conn_pts)
        return self._connectionPtShape

    def get_connection_points(self):
        pass

    def get_connection_point_at(self, pos):
        _conn_pts = self.get_connection_points()
        _lst_conn_pts = np.array([x[1] for x in _conn_pts])
        _closest_pt_idx = utils.util_find_closest_pt_idx(_lst_conn_pts, pos)
        _closest_pt = _lst_conn_pts[_closest_pt_idx]
        if math.dist(_closest_pt, pos) <= self.minConnPtDistance:
            return _closest_pt, _conn_pts[_closest_pt_idx][0]
        else:
            return None, (0, 0)


class StateChartTransition(Serializable, DrawObjectGroup):
    def __init__(self, in_foreground=False, is_visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=is_visible)
        Serializable.__init__(self)
        self.uuid = None
        self.role = EnumItemRole.ITEM_TRANSITION
        self.shapeStyle = EnumShapeStyle.STYLE_DEFAULT
        self.isSelected = False

    def has_style(self, style):
        return (self.shapeStyle & style) != 0

    def add_style(self, style):
        self.shapeStyle |= style
