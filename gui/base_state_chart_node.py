import math
import numpy as np
from .define_gui import *
from wxgraph import DrawObjectPointSet
from wxgraph import util_bbox, DrawObjectGroup, utils


class StateChartNode(DrawObjectGroup):
    CONN_PT_SHAPE_DIAMETER = 4

    def __init__(self, in_foreground=False, is_visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=is_visible)
        self.uuid = None
        self.role = ''
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

    def add_in_wire(self, wire):
        self.inWires.append(wire)

    def add_out_wire(self, wire):
        self.outWires.append(wire)

    def remove_in_wire(self, wire):
        if wire in self.inWires:
            self.inWires.remove(wire)

    def remove_out_wire(self, wire):
        if wire in self.outWires:
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


class StateChartTransition(DrawObjectGroup):
    def __init__(self, in_foreground=False, is_visible=True):
        DrawObjectGroup.__init__(self, in_foreground=in_foreground, is_visible=is_visible)
        self.uuid = None
        self.role = ''
        self.shapeStyle = EnumShapeStyle.STYLE_DEFAULT
        self.isSelected = False

    def has_style(self, style):
        return (self.shapeStyle & style) != 0

    def add_style(self, style):
        self.shapeStyle |= style
