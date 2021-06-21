import math, copy
import wx
import numpy as N
from wxgraph import (DrawObjectGroup,
                     DrawObjectScaledTextBox,
                     DrawObjectArrow,
                     DrawObjectSquarePoint,
                     DrawObjectLine)
from .define_gui import *
from .base_state_chart_node import StateChartNode, StateChartTransition
import wxgraph.util_bbox as bbox
from wxgraph.utils import util_angle_between_degree, util_find_closest_pt_idx


class TransitionWireShape(StateChartTransition):
    CTRL_PT_SIZE = 8
    WIRE_BASE_LINE_OK_COLOR = '#0AB0AB'
    WIRE_BASE_LINE_NOK_COLOR = '#AAAAAA'
    WIRE_BASE_LINE_WIDTH = 2
    WIRE_BASE_LINE_NOK_STYLE = 'ShortDash'
    WIRE_BASE_LINE_OK_STYLE = 'Solid'

    def __init__(self, src_pt=N.array((0, 0)), dst_pt=N.array((0, 0)), text='Untitled Transition', in_foreground=False,
                 visible=True):
        StateChartTransition.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self.hitLineWidth = 5
        self.srcPt = src_pt
        self.dstPt = dst_pt
        self.srcNode = None
        self.dstNode = None
        self._hitCbsBackup = None
        self.wayPoints = list()
        self.currentSelectedCtrlPtIdx = -1
        self.text = text
        self.textBox = DrawObjectScaledTextBox(text, src_pt, 8, align='cc')
        self.baseLine = DrawObjectLine([src_pt, dst_pt], line_width=self.WIRE_BASE_LINE_WIDTH)
        self.arrow = DrawObjectArrow(src_pt, 0, 0, arrow_head_size=12,
                                     line_width=self.WIRE_BASE_LINE_WIDTH,
                                     line_color=self.WIRE_BASE_LINE_NOK_COLOR)
        self.add_object(self.textBox)
        self.add_object(self.baseLine)
        self.add_object(self.arrow)
        self._update_transition_text_position()
        self._calc_way_point()

    def serialize(self):
        _d = dict()
        _d.update({'class': self.__class__.__name__})
        _d.update({'uuid': self.uuid})
        _d.update({'role': self.role})
        _d.update({'text': self.text})
        _d.update({'isVisible': self.isVisible})
        _d.update({'srcPosition': self.srcPt})
        _d.update({'dstPosition': self.dstPt})
        _d.update({'wayPoint': self.wayPoints})
        _d.update({'srcNodeUUID': self.srcNode.uuid if self.srcNode else None})
        _d.update({'dstNodeUUID': self.dstNode.uuid if self.dstNode else None})
        _d.update({'arrowAngle': self.arrow.arrowHeadAngle})
        _d.update({'arrowDirection': self.arrow.direction})
        return _d

    def set_connection_invalid_style(self):
        self.baseLine.set_line_style(self.WIRE_BASE_LINE_NOK_STYLE)
        self.baseLine.set_line_color(self.WIRE_BASE_LINE_NOK_COLOR)
        self.arrow.set_line_color(self.WIRE_BASE_LINE_NOK_COLOR)

    def set_connection_valid_style(self):
        self.baseLine.set_line_style(self.WIRE_BASE_LINE_OK_STYLE)
        self.baseLine.set_line_color(self.WIRE_BASE_LINE_OK_COLOR)
        self.arrow.set_line_color(self.WIRE_BASE_LINE_OK_COLOR)

    def set_line_style(self, style):
        self.baseLine.set_line_style(style)

    def move_control_point(self, pt_diff, idx=None):
        if idx is None:
            idx = self.currentSelectedCtrlPtIdx
        if idx == -1:
            return
        if 0 == idx:
            _pt = N.array(self.srcPt + pt_diff, N.float)
            self.set_src_point(_pt)
        elif 1 == idx:
            self.wayPoints[1] += pt_diff
        elif 2 == idx:
            _pt = N.array(self.dstPt + pt_diff, N.float)
            self.set_dst_point(_pt)
        _pts = [self.srcPt]
        _pts.extend(self.wayPoints)
        _pts.append(self.dstPt)
        self.baseLine.set_points(_pts)

    def guess_control_point(self, pt):
        _ctrl_pts = self.get_control_points()
        _idx = util_find_closest_pt_idx(_ctrl_pts, pt)
        _ctrl_pt = _ctrl_pts[_idx]
        # calculate the distance to this closest point
        # if distance shorter than the radius the this is the pt.
        if math.dist(_ctrl_pt, pt) <= self.CTRL_PT_SIZE:
            self.currentSelectedCtrlPtIdx = _idx

    def get_control_points(self):
        return [self.srcPt, self.wayPoints[1], self.dstPt]

    def get_control_points_length(self):
        return 3

    def set_src_point(self, src_pt):
        self.srcPt = src_pt
        self._calc_way_point()
        self._update_base_line()
        self._update_transition_text_position()
        self._update_arrow()

    def set_dst_point(self, dst_pt):
        self.dstPt = dst_pt
        # _prev_pts = self.arrowLine.Points
        self._calc_way_point()
        self._update_base_line()
        self._update_transition_text_position()
        self._update_arrow()

    def save_hit(self):
        self._hitCbsBackup = dict()
        for evt, cb in self.callBackFuncs.items():
            self._hitCbsBackup.update({evt: cb})

    def restore_hit(self):
        if self._hitCbsBackup:
            for evt, cb in self._hitCbsBackup.items():
                self.bind(evt, cb)

    def _update_base_line(self):
        _pts = list()
        _pts.append(self.srcPt)
        _pts.extend(self.wayPoints)
        _pts.append(self.dstPt)
        self.baseLine.set_points(_pts)

    def _update_transition_text_position(self):
        self.textBox.set_position((self.srcPt + self.dstPt) / 2)

    def _update_arrow(self):
        self.arrow.set_position(self.dstPt)
        if self.dstNode is None:
            _calc_angle_trg_pt = self.baseLine.points[1]
            _calc_angle_src_pt = self.dstPt
        else:
            _calc_angle_trg_pt = self.baseLine.points[-2]
            _calc_angle_src_pt = self.dstPt
        _angel_deg = math.degrees(math.atan2(_calc_angle_trg_pt[1] - _calc_angle_src_pt[1],
                                             _calc_angle_trg_pt[0] - _calc_angle_src_pt[0]))
        self.arrow.set_direction(-1 * (90 + _angel_deg))

    def _calc_way_point(self):
        self.wayPoints.clear()
        if self.srcNode is not None:
            _conn_pts, _src_nv = self.srcNode.get_connection_point_at(self.srcPt)
        else:
            _src_nv = (0, 0)
        _pt_src_cpt = self.srcPt + (_src_nv[0] * (self.arrow.arrowHeadSize + 5),
                                    _src_nv[1] * (self.arrow.arrowHeadSize + 5))
        if self.dstNode is not None:
            _conn_pts, _dst_nv = self.dstNode.get_connection_point_at(self.dstPt)
        else:
            _dst_nv = (0, 0)
        _pt_dst_cpt = self.dstPt + (_dst_nv[0] * (self.arrow.arrowHeadSize + 5),
                                    _dst_nv[1] * (self.arrow.arrowHeadSize + 5))
        self.wayPoints.append(_pt_src_cpt)
        _bb = bbox.from_points([_pt_src_cpt, _pt_dst_cpt])
        self.wayPoints.append(_bb.center)
        if not N.array_equal(_pt_dst_cpt, self.dstPt):
            self.wayPoints.append(_pt_dst_cpt)
        # _sign_x = 1 if self.dstPt[0] >= _pt_c1[0] else -1
        # _sign_y = 1 if self.dstPt[1] >= _pt_c1[1] else -1

    def deserialize(self):
        # todo: add serialize for all node
        pass

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('transition on_enter')

    def on_leave(self):
        print('transition on_leave')

    def on_left_up(self):
        print('transition on left up')
