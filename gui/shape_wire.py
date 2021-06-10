import wx
from wx.lib.floatcanvas import FloatCanvas
from wx.lib.floatcanvas.FCObjects import Group, ScaledTextBox, ArrowLine
from .define_gui import *
from .base_state_chart_node import StateChartNode


class WireShape(Group, StateChartNode):
    def __init__(self, src_pt, dst_pt, in_foreground=False, visible=True):
        Group.__init__(self, InForeground=in_foreground, IsVisible=visible)
        StateChartNode.__init__(self)
        self.connectionStyle = EnumShapeConnectionStyle.NONE
        self.srcPt = src_pt
        self.dstPt = dst_pt
        self.textBox = ScaledTextBox('Text', src_pt, 8)
        self.arrowLine = ArrowLine([src_pt, dst_pt], ArrowHeadSize=12, LineWidth=1)
        self.AddObject(self.textBox)
        self.AddObject(self.arrowLine)

    def set_line_style(self, style):
        self.arrowLine.SetLineStyle(style)

    def set_src_point(self, src_pt):
        self.srcPt = src_pt
        _prev_pts = self.arrowLine.Points
        _prev_pts[0] = src_pt
        self.arrowLine.SetPoints(_prev_pts)
        self.arrowLine.CalcArrowPoints()

    def set_dst_point(self, dst_pt):
        self.dstPt = dst_pt
        #_prev_pts = self.arrowLine.Points
        _ctrl_pts=self._calc_control_point()
        _pts=list()
        _pts.append(self.srcPt)
        _pts.extend(list(_ctrl_pts))
        _pts.append(self.dstPt)
        self.arrowLine.SetPoints(_pts)
        self.arrowLine.CalcArrowPoints()

    def _calc_control_point(self):
        _ctr_offset_y1, _ctr_offset_y2 = self.srcPt[1], self.dstPt[1]
        _tangent = min(abs(_ctr_offset_y1 - _ctr_offset_y2),10)
        _ctr_offset_y1 -= _tangent
        _ctr_offset_y2 += _tangent
        _ctrl_pt1 = wx.RealPoint(self.srcPt[0], _ctr_offset_y1)
        _ctrl_pt2 = wx.RealPoint(self.dstPt[0], _ctr_offset_y2)
        return _ctrl_pt1, _ctrl_pt2

    def on_left_down(self):
        print('state left down')

    def on_enter(self):
        print('state on_enter')

    def on_leave(self):
        print('state on_leave')

    def on_left_up(self):
        print('state on left up')
