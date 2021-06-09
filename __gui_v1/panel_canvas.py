import time
import wx
import wx.adv
import wx.lib.agw.aui as aui
import json
from __gui_v1.define_gui import *
from application.define import EnumPanelRole
from application.shape_wire import WireNodeShape
from application.shape_node import BaseNodeShape
from application.shape_state_node import StateNodeShape, StateInitNodeShape, StateFinalNodeShape
from .utils_helper import *


# todo: canvas scale, selection, selected
# todo: scroll, middlekey move


class CanvasSetting:
    def __init__(self):
        self.mGCDCEnabled = False
        self.mFScale = 1.0
        self.mFMinScale = 0.2
        self.mFMaxScale = 4.0
        self.mStyle = EnumCanvasStyle.STYLE_DEFAULT
        self.mBackgroundColor: wx.Colour = wx.Colour(240, 240, 240)
        self.mCommonHoverColor: wx.Colour = wx.Colour(120, 120, 255)
        self.mGradientFrom: wx.Colour = wx.Colour(240, 240, 240)
        self.mGradientTo: wx.Colour = wx.Colour(200, 200, 255)
        self.mGridSize: wx.Size = wx.Size(20, 20)
        self.mGridLineMult: int = 5
        self.mGridColor: wx.Colour = wx.Colour(200, 200, 200)
        self.mGridStyle: int = wx.SHORT_DASH
        self.mShadowOffset: wx.RealPoint = wx.RealPoint(4, 4)
        self.mShadowFill: wx.Brush = wx.Brush(wx.Colour(150, 150, 150, 128), wx.BRUSHSTYLE_SOLID)
        # self.mLstAcceptedShapes = list()
        # self.mIPrintHAlign: int = EnumHAlign.halignCENTER
        # self.mIPrintVAlign: int = EnumVAlign.valignMIDDLE
        # self.mIPrintMode: int = EnumPrintMode.prnFIT_TO_MARGINS


class StateChartCanvasViewPanel(wx.Panel):
    def __init__(self, parent, wx_id, size=wx.DefaultSize, pos=wx.DefaultPosition):
        wx.Panel.__init__(self, parent, wx_id, pos, size)
        self.uuid = None
        self.role = EnumPanelRole.STATE_CHART_CANVAS
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.toolbarIconSize = wx.Size(16, 16)
        self.canvas = Canvas(self, wx.ID_ANY)
        self.canvasToolbar = self._create_toolbar()
        self.mainSizer.Add(self.canvasToolbar, 0, wx.EXPAND)
        self.mainSizer.Add(self.canvas, 1, wx.EXPAND)
        self._bind_event()
        self.SetSizer(self.mainSizer)
        self.Layout()

    def _create_toolbar(self):
        _tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        _tb.SetToolBitmapSize(self.toolbarIconSize)
        _pointer_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_pointer_bk.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _state_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_state.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _state_sub_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_substate.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _init_state_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_initstate.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _final_state_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_finalstate.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _wire_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_wire.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _note_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_note.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.toolbarIconSize).ConvertToBitmap()
        _tb_pointer = wx.NewIdRef()
        _tb_state = wx.NewIdRef()
        _tb_sub_state = wx.NewIdRef()
        _tb_init_state = wx.NewIdRef()
        _tb_final_state = wx.NewIdRef()
        _tb_wire_state = wx.NewIdRef()
        _tb_note = wx.NewIdRef()
        _tb.AddRadioTool(_tb_pointer, "Pointer", _pointer_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='Pointer',
                         client_data=EnumCanvasToolbarMode.POINTER)
        _tb.AddRadioTool(_tb_state, "State", _state_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='State',
                         client_data=EnumCanvasToolbarMode.STATE)
        _tb.AddRadioTool(_tb_sub_state, "Sub State", _state_sub_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='Sub State',
                         client_data=EnumCanvasToolbarMode.SUB_STATE)
        _tb.AddRadioTool(_tb_init_state, "Init State", _init_state_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='Init State',
                         client_data=EnumCanvasToolbarMode.INIT_STATE)
        _tb.AddRadioTool(_tb_final_state, "Final State", _final_state_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='Final State',
                         client_data=EnumCanvasToolbarMode.FINAL_STATE)
        _tb.AddRadioTool(_tb_wire_state, "Connection", _wire_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='Connection',
                         client_data=EnumCanvasToolbarMode.CONNECTION)
        _tb.AddRadioTool(_tb_note, "Note", _note_shape_icon,
                         disabled_bitmap=wx.NullBitmap, short_help_string='Note',
                         client_data=EnumCanvasToolbarMode.NOTE)
        _tb.AddSeparator()
        _tb.Realize()
        self.Bind(wx.EVT_TOOL,
                  lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.POINTER),
                  _tb_pointer)
        self.Bind(wx.EVT_TOOL,
                  lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.STATE), _tb_state)
        self.Bind(wx.EVT_TOOL,
                  lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.SUB_STATE),
                  _tb_sub_state)
        self.Bind(wx.EVT_TOOL,
                  lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.INIT_STATE),
                  _tb_init_state)
        self.Bind(wx.EVT_TOOL,
                  lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.FINAL_STATE),
                  _tb_final_state)
        self.Bind(wx.EVT_TOOL,
                  lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.CONNECTION),
                  _tb_wire_state)
        self.Bind(wx.EVT_TOOL, lambda evt: self.on_tool_changed(evt, EnumCanvasToolbarMode.NOTE),
                  _tb_note)
        _tb.ToggleTool(_tb_pointer, True)
        self.on_tool_changed(None, EnumCanvasToolbarMode.POINTER)
        return _tb

    def _bind_event(self):
        pass

    def on_tool_changed(self, evt, flag):
        self.canvas.set_canvas_tool_mode(flag)

    def process_key_down(self, k_code):
        if k_code == wx.WXK_ESCAPE:
            _tool = self.canvasToolbar.FindToolByIndex(EnumCanvasToolbarMode.POINTER)
            if _tool is not None:
                self.canvasToolbar.ToggleTool(_tool.GetId(), True)
                self.on_tool_changed(None, EnumCanvasToolbarMode.POINTER)
                self.canvasToolbar.Refresh()


class CanvasRepositionModifier:
    def __init__(self, item, org_pos):
        self._item = item
        self._orgPos = org_pos
        self._curPos = org_pos
        self.mouseOffset = wx.Point(0, 0)
        self._modifiedRect = wx.Rect()
        self.inWires = None
        self.outWires = None

    def get_item(self):
        return self._item

    def get_org_position(self):
        return self._orgPos

    def get_current_position(self):
        return self._curPos

    def get_position_diff(self, reverse=False):
        if reverse:
            return self._orgPos - self._curPos
        return self._curPos - self._orgPos

    def update_position(self, pos):
        if self._item is None:
            return
        _bb = self._item.get_bounding_box()
        self._curPos = pos
        self._modifiedRect = self._modifiedRect.Union(wx.Rect(pos, _bb.GetSize()))

    def get_modified_bounding_box(self):
        return self._modifiedRect


class CanvasPanModifier:
    def __init__(self, start_at):
        self.startPos = start_at
        self.curPos = start_at
        self.prevCursor = None

    def get_previous_cursor(self):
        return self.prevCursor

    def set_previous_cursor(self, cursor):
        self.prevCursor = cursor

    def update_position(self, pos):
        self.curPos = pos

    def get_diff(self, reverse=False):
        if not reverse:
            return self.curPos - self.startPos
        else:
            return self.startPos - self.curPos


class CanvasConnectionModifier:
    def __init__(self, src_node):
        self.srcNode = src_node
        self.dstNode = None
        self.srcPort = None
        self.tmpWire = None
        self.lastPnt = wx.Point(0, 0)


class Canvas(wx.ScrolledWindow):
    # todo: scale the canvas
    def __init__(self, parent, wx_id, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, wx_id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.setting = CanvasSetting()
        self.currentProcessingItem = None
        self.nodes = dict()
        self.wires = dict()
        self.repositionModifier = None
        self.panScrollModifier = None
        self.connectionModifier = None
        # ui initial setting
        self.maxWidth = CANVAS_MAX_W
        self.maxHeight = CANVAS_MAX_H
        self.canvasToolbarMode = EnumCanvasToolbarMode.POINTER
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20, 20)
        # better ui
        # self.SetScrollbars(5, 5, 100, 100)
        # self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)
        # create a PseudoDC to record our drawing
        self.pdc = wx.adv.PseudoDC()
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_middle_up)

    def get_style(self):
        return self.setting.mStyle

    def add_style(self, style):
        self.setting.mStyle |= style

    def remove_style(self, style):
        self.setting.mStyle &= ~style

    def has_style(self, style):
        return (self.setting.mStyle & style) != 0

    def get_scale(self):
        return self.setting.mFScale

    def get_canvas_tool_mode(self):
        return self.canvasToolbarMode

    def set_canvas_tool_mode(self, mode: EnumCanvasToolbarMode):
        print('mode=', mode)
        self.canvasToolbarMode = mode

    def set_scale(self, scale):
        if scale != 0:
            self.setting.mFScale = scale
        else:
            self.setting.mFScale = 1
        for nid, node in self.nodes.items():
            node.scale(self.setting.mFScale, self.setting.mFScale)
        # self.update_virtual_size()
        self.Refresh(False)

    def on_resize(self, evt):
        if self.has_style(EnumCanvasStyle.STYLE_GRADIENT_BACKGROUND):
            self.Refresh(False)
        evt.Skip()

    def on_middle_down(self, evt: wx.MouseEvent):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        if not evt.LeftDown():
            self.panScrollModifier = CanvasPanModifier(_pt)
            self.panScrollModifier.set_previous_cursor(self.GetCursor())
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        evt.Skip()

    def on_middle_up(self, evt):
        _previous_cursor = self.panScrollModifier.get_previous_cursor()
        self.SetCursor(_previous_cursor)
        self.panScrollModifier = None
        evt.Skip()

    def on_mouse_wheel(self, evt: wx.MouseEvent):
        if evt.ControlDown():
            _scale = self.setting.mFScale
            _scale += evt.GetWheelRotation() / (evt.GetWheelDelta() * 10)
            if _scale < self.setting.mFMinScale: _scale = self.setting.mFMinScale
            if _scale > self.setting.mFMaxScale: _scale = self.setting.mFMaxScale
            # self.set_scale(_scale)
        else:
            evt.Skip()

    def on_key_down(self, evt: wx.KeyEvent):
        _k_code = evt.GetKeyCode()
        _parent = self.GetParent()
        if _parent:
            _parent.process_key_down(_k_code)
        evt.Skip()

    def on_key_up(self, evt):
        # print('canvas key_up')
        evt.Skip()

    def on_scroll(self, evt):

        print('scroll', evt)
        # print(wx.GetKeyState(wx.WXK_CONTROL))
        evt.Skip()

    def convert_coords(self, pt):
        _x_view, _y_view = self.GetViewStart()
        _x_delta, _y_delta = self.GetScrollPixelsPerUnit()
        return wx.Point((pt[0] + (_x_view * _x_delta)) / self.setting.mFScale,
                        (pt[1] + (_y_view * _y_delta)) / self.setting.mFScale)

    def offset_rect(self, rect):
        # fixme: drop move down, the rect becomes smaller???? why
        _x_view, _y_view = self.GetViewStart()
        _x_delta, _y_delta = self.GetScrollPixelsPerUnit()
        rect.Offset(-(_x_view * _x_delta) * self.setting.mFScale, -(_y_view * _y_delta) * self.setting.mFScale)
        rect.SetWidth(rect.GetWidth() * self.setting.mFScale)
        rect.SetHeight(rect.GetHeight() * self.setting.mFScale)

    def add_item(self, item: BaseNodeShape):
        _nid = item.get_id()
        self.pdc.SetId(_nid)
        item.draw(self.pdc)
        self.pdc.SetIdBounds(_nid, item.get_bounding_box())
        self.nodes[_nid] = item

    def get_wires_by_item_id(self, item_id):
        _w_in = list()
        _w_out = list()
        for path, wire in self.wires.items():
            if '_%s' % item_id in path:
                _w_in.append(wire)
            if '%s_' % item_id in path:
                _w_out.append(wire)
        return _w_in, _w_out

    def on_left_down(self, evt):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        _mode = self.canvasToolbarMode
        _hit_item = self.HitTest(_win_pt)
        if _mode == EnumCanvasToolbarMode.POINTER:
            if _hit_item is not None:
                if _hit_item.has_style(EnumShapeStyle.REPOSITION):
                    self.repositionModifier = CanvasRepositionModifier(_hit_item, _win_pt)
                    self.repositionModifier.update_position(_win_pt)
                    self.repositionModifier.mouseOffset = _win_pt - _hit_item.position
                    _in_wire, _out_wire = self.get_wires_by_item_id(_hit_item.get_id())
                    self.repositionModifier.inWires = _in_wire
                    self.repositionModifier.outWires = _out_wire
        elif _mode == EnumCanvasToolbarMode.CONNECTION:
            if self.connectionModifier is None and _hit_item is not None:
                if isinstance(_hit_item, (StateNodeShape,StateInitNodeShape)):
                    self.connectionModifier = CanvasConnectionModifier(_hit_item)
                    _node_conn_style = self.connectionModifier.srcNode.get_connection_style()
                    if _node_conn_style == EnumShapeConnectionStyle.ANYWHERE:
                        self.connectionModifier.lastPnt = _win_pt
                        self.connectionModifier.tmpWire = WireNodeShape(self, wx.ID_ANY)
                        self.connectionModifier.tmpWire.borderPen.SetStyle(wx.PENSTYLE_SHORT_DASH)
                        self.connectionModifier.tmpWire.borderPen.SetWidth(2)
                    elif _node_conn_style == EnumShapeConnectionStyle.ONLY_ON_PORT:
                        self.connectionModifier.srcPort = self.srcNode.HitTest(_win_pt.x, _win_pt.y)
                        if self.connectionModifier.srcPort is not None:
                            self.connectionModifier.srcPort.Disconnect()
                            self.connectionModifier.tmpWire = WireShape(
                                self.srcNode.GetRect().GetPosition() + self.srcPort.GetPosition(), _pt,
                                self.srcPort.GetType())
                    elif _node_conn_style == EnumShapeConnectionStyle.NONE:
                        self.connectionModifier.lastPnt = _pt
        else:
            if _mode == EnumCanvasToolbarMode.STATE:
                self.currentProcessingItem = StateNodeShape(self, size=wx.Size(100, 50), pos=_win_pt)
            elif _mode == EnumCanvasToolbarMode.SUB_STATE:
                pass
            elif _mode == EnumCanvasToolbarMode.INIT_STATE:
                self.currentProcessingItem = StateInitNodeShape(self, size=wx.Size(18, 18), pos=_win_pt)
            elif _mode == EnumCanvasToolbarMode.FINAL_STATE:
                self.currentProcessingItem = StateFinalNodeShape(self, size=wx.Size(18, 18), pos=_win_pt)
        evt.Skip()

    def on_motion(self, evt: wx.MouseEvent):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        _mode = self.canvasToolbarMode
        _hit_item = self.HitTest(_win_pt)
        if _mode == EnumCanvasToolbarMode.POINTER:
            # handle hover event
            if not evt.Dragging():
                pass
                if _hit_item:
                    # handle the hit item hovered
                    _id = _hit_item.get_id()
                    if not _hit_item.isMouseOvered:
                        _hit_item.isMouseOvered = True
                        _hit_item.draw(self.pdc)
                        _rect = self.pdc.GetIdBounds(_id)
                        self.offset_rect(_rect)
                        self.RefreshRect(_rect, False)
                else:
                    # handle the hovered item unhovered
                    for k, v in self.nodes.items():
                        if v.isMouseOvered:
                            v.isMouseOvered = False
                            v.draw(self.pdc)
                            _rect = self.pdc.GetIdBounds(v.get_id())
                            self.offset_rect(_rect)
                            self.RefreshRect(_rect, False)

            else:
                # handle the canvas move while middle dragging
                if self.panScrollModifier is not None:
                    self.panScrollModifier.update_position(_pt)
                    _diff = self.panScrollModifier.get_diff(reverse=True)
                    _win_diff = self.convert_coords(_diff)
                    _x_per, _y_per = self.GetScrollPixelsPerUnit()
                    _x_scroll_pos = math.floor(_win_diff.x / _x_per)
                    _y_scroll_pos = math.floor(_win_diff.y / _y_per)
                    if _x_scroll_pos < 0: _x_scroll_pos = 0
                    if _y_scroll_pos < 0: _y_scroll_pos = 0
                    self.Scroll(_x_scroll_pos, _y_scroll_pos)
                # handle the shape move
                if self.repositionModifier is not None:
                    self.repositionModifier.update_position(_win_pt)
                    _diff = self.repositionModifier.get_position_diff()
                    _item = self.repositionModifier.get_item()
                    self._redraw_node_at(_item, _win_pt - self.repositionModifier.mouseOffset)
                    if self.repositionModifier.inWires is not None:
                        for wire in self.repositionModifier.inWires:
                            _pt = wire.prevDstPoint + _diff
                            self._redraw_wire_at(wire, wire.srcPoint, _pt)
                    if self.repositionModifier.outWires is not None:
                        for wire in self.repositionModifier.outWires:
                            _pt = wire.prevSrcPoint + _diff
                            self._redraw_wire_at(wire, _pt, wire.dstPoint)

        elif _mode == EnumCanvasToolbarMode.CONNECTION:
            if evt.Dragging() and self.connectionModifier is not None:
                # handle the mouse motion in connection mode
                _src_node_conn_style = self.connectionModifier.srcNode.get_connection_style()
                if _src_node_conn_style == EnumShapeConnectionStyle.ANYWHERE:
                    if not self.connectionModifier.srcNode.contains(_win_pt):
                        _intersection_pt = self.connectionModifier.srcNode.get_bb_intersection_point_along_center(
                            _win_pt)
                        if _intersection_pt:
                            self.connectionModifier.lastPnt = _intersection_pt
                            self._redraw_wire_at(self.connectionModifier.tmpWire, _intersection_pt, _win_pt)
                if _hit_item:
                    if isinstance(_hit_item, (StateNodeShape,StateFinalNodeShape)):
                        self.connectionModifier.dstNode = _hit_item
                        _dst_node_conn_style = _hit_item.get_connection_style()
                        if _dst_node_conn_style == EnumShapeConnectionStyle.ANYWHERE:
                            if self.connectionModifier.tmpWire and _hit_item.contains(_win_pt):
                                self.connectionModifier.tmpWire.borderPen.SetStyle(wx.PENSTYLE_SOLID)
                else:
                    if self.connectionModifier.tmpWire:
                        self.connectionModifier.tmpWire.borderPen.SetStyle(wx.PENSTYLE_SHORT_DASH)

        evt.Skip()

    def on_left_up(self, evt):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        _hit_item = self.HitTest(_win_pt)
        if self.canvasToolbarMode in [EnumCanvasToolbarMode.STATE,
                                      EnumCanvasToolbarMode.SUB_STATE,
                                      EnumCanvasToolbarMode.INIT_STATE,
                                      EnumCanvasToolbarMode.FINAL_STATE]:
            if self.currentProcessingItem is not None:
                self.currentProcessingItem.set_position(_win_pt)
                self.add_item(self.currentProcessingItem)
                self.Refresh(False)
        # Attempt to make a connection.
        elif self.canvasToolbarMode == EnumCanvasToolbarMode.CONNECTION:
            if _hit_item is not None:
                if self.connectionModifier is not None and isinstance(_hit_item, (StateNodeShape,StateFinalNodeShape)):
                    self.connectionModifier.dstNode = _hit_item
                    _node_conn_style = self.connectionModifier.dstNode.get_connection_style()
                    if _node_conn_style == EnumShapeConnectionStyle.ANYWHERE:
                        _intersection_pt = _hit_item.get_bb_intersection_point_along_center(_win_pt,
                                                                                            include_extend=True)
                        if _intersection_pt is not None:
                            _src_node_id = self.connectionModifier.srcNode.get_id()
                            _dst_node_id = _hit_item.get_id()
                            _wire = WireNodeShape(self, wx.ID_ANY, self.connectionModifier.lastPnt, _intersection_pt)
                            _wire.srcNodeId = _src_node_id
                            _wire.dstNodeId = _dst_node_id
                            _wire.borderPen.SetStyle(wx.PENSTYLE_SOLID)
                            _wire.borderPen.SetWidth(2)
                            self.add_item(_wire)
                            _wire_k = '%s_%s' % (_src_node_id, _dst_node_id)
                            self.wires.update({_wire_k: _wire})
                    elif _node_conn_style == EnumShapeConnectionStyle.ONLY_ON_PORT:
                        _dst_port = _hit_item.HitTest(_win_pt.x, _win_pt.y)
                        if _dst_port is not None and (
                                self.connectionModifier.srcPort.GetType() != _dst_port.GetType()) and (
                                self.connectionModifier.srcNode.GetId() != _dst_port.GetId()):
                            self.connectionModifier.srcPort.Connect(_dst_port)

            # Erase the temp wire.
            if self.connectionModifier is not None:
                if self.connectionModifier.tmpWire is not None:
                    _rect = self.pdc.GetIdBounds(self.connectionModifier.tmpWire.get_id())
                    self.pdc.RemoveId(self.connectionModifier.tmpWire.get_id())
                    self.offset_rect(_rect)
                    self.RefreshRect(_rect, False)
                self.connectionModifier = None
        elif self.canvasToolbarMode == EnumCanvasToolbarMode.POINTER:
            if self.repositionModifier is not None:
                if self.repositionModifier.inWires is not None:
                    for wire in self.repositionModifier.inWires:
                        wire.prevDstPoint = wire.dstPoint
                        wire.prevSrcPoint = wire.srcPoint
                if self.repositionModifier.outWires is not None:
                    for wire in self.repositionModifier.outWires:
                        wire.prevDstPoint = wire.dstPoint
                        wire.prevSrcPoint = wire.srcPoint
                self.repositionModifier = None

        evt.Skip()

    def HitTest(self, pt):
        _ids = self.pdc.FindObjects(pt[0], pt[1], CANVAS_HIT_RADIUS)
        _hits = [idx for idx in _ids if idx in self.nodes]
        return self.nodes[_hits[0]] if _hits else None

    def on_paint(self, event):
        _t1 = time.time()
        # Create a buffered paint DC.  It will create the real wx.PaintDC and
        # then blit the bitmap to it when dc is deleted.
        _dc = wx.AutoBufferedPaintDC(self)
        if self.setting.mGCDCEnabled:
            _dc = wx.GCDC(_dc)
        # Use PrepareDC to set position correctly.
        self.PrepareDC(_dc)
        _dc.SetUserScale(self.setting.mFScale, self.setting.mFScale)

        # draw the background
        self.draw_background(_dc)
        # Create a clipping rect from our position and size and the Update Region.
        _xv, _yv = self.GetViewStart()
        _dx, _dy = self.GetScrollPixelsPerUnit()
        _x, _y = (_xv * _dx, _yv * _dy)

        _rgn = self.GetUpdateRegion()
        if _rgn.IsEmpty():
            return
        _rgn.Offset(_x, _y)
        _rect = _rgn.GetBox()
        # Draw to the dc using the calculated clipping rect.
        # _dc.SetPen(wx.RED_PEN)
        # _dc.SetBrush(wx.TRANSPARENT_BRUSH)
        # _dc.DrawText('Scale:%.2F,update(w|h):%s,%s' % (self.setting.mFScale, _rect.GetWidth(), _rect.GetHeight()), _x,
        #              _y)
        # _dc.DrawRectangle(_rect)
        self.pdc.DrawToDCClipped(_dc, _rect)
        print('repaint use %.2F ms' % ((time.time() - _t1) * 100))

    def draw_background(self, dc):
        # erase the background
        if self.has_style(EnumCanvasStyle.STYLE_GRADIENT_BACKGROUND):
            _bk_size = self.GetVirtualSize() + wx.Size(self.setting.mGridSize.x, self.setting.mGridSize.y)
            if self.setting.mFScale != 1.0:
                # dc.GradientFillLinear(wx.Rect(wx.Point(0, 0),
                #                               wx.Size(_bk_size.x / self.setting.mFScale,
                #                                       _bk_size.y / self.setting.mFScale)),
                #                       self.setting.mGradientFrom, self.setting.mGradientTo, wx.SOUTH)
                dc.GradientFillLinear(wx.Rect(wx.Point(0, 0), wx.Size(_bk_size.x, _bk_size.y)),
                                      self.setting.mGradientFrom, self.setting.mGradientTo, wx.SOUTH)
            else:
                dc.GradientFillLinear(wx.Rect(wx.Point(0, 0), _bk_size),
                                      self.setting.mGradientFrom, self.setting.mGradientTo, wx.SOUTH)
        else:
            _brush = wx.Brush(self.setting.mBackgroundColor)
            dc.SetBackground(_brush)
            dc.Clear()
        # draw the grid
        if self.has_style(EnumCanvasStyle.STYLE_SHOW_GRID):
            _line_dist = self.setting.mGridSize.x * self.setting.mGridLineMult
            if _line_dist * self.setting.mFScale > 3:
                _grid_rect = wx.Rect(wx.Point(0, 0), self.GetVirtualSize() + self.setting.mGridSize)
                _max_x = int(_grid_rect.GetRight() / self.setting.mFScale)
                _max_y = int(_grid_rect.GetBottom() / self.setting.mFScale)
                dc.SetPen(wx.Pen(self.setting.mGridColor, 1, self.setting.mGridStyle))
                for x in range(_grid_rect.GetLeft(), _max_x, _line_dist):
                    dc.DrawLine(x, 0, x, _max_y)
                for y in range(_grid_rect.GetTop(), _max_y, _line_dist):
                    dc.DrawLine(0, y, _max_x, y)

    def _redraw_wire_at(self, wire, pt1=None, pt2=None):
        _rect1 = wire.get_bounding_box()
        if pt1 is not None:
            wire.srcPoint = pt1
        if pt2 is not None:
            wire.dstPoint = pt2
        _rect2 = wire.get_bounding_box()
        _rect = _rect1.Union(_rect2)
        self.offset_rect(_rect)
        self.pdc.ClearId(wire.get_id())
        wire.draw(self.pdc)
        self.RefreshRect(_rect, False)

    def _redraw_node_at(self, node, pt=None):
        _rect1 = node.get_bounding_box()
        node.set_position(pt)
        _rect2 = node.get_bounding_box()
        _rect = _rect1.Union(_rect2)
        self.offset_rect(_rect)
        # before redraw the id must be cleared, then call draw
        self.pdc.ClearId(node.get_id())
        for x in node.get_children_list():
            self.pdc.ClearId(x.get_id())
        node.draw(self.pdc)
        self.RefreshRect(_rect, False)

    def load(self, filePath):
        with open(filePath, 'r') as f:
            data = json.load(f)
            for nodeData in data:
                props = nodeData['properties']
                node = self.add_item(
                    props['name'],
                    wx.Point(props['x'], props['y']),
                    nodeData['ins'].keys(),
                    nodeData['outs'].keys(),
                    props['color']
                )

    def get_node_port(self, node, port):
        return node.GetPorts(port)
