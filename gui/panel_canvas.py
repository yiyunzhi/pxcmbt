import time
import wx
import wx.adv
import wx.lib.agw.aui as aui
import json
from gui.define_gui import *
from application.define import EnumPanelRole
from application.shape_wire import WireShape
from application.shape_node import BaseNodeShape
from application.shape_state_node import StateNodeShape


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


class Canvas(wx.ScrolledWindow):
    def __init__(self, parent, wx_id, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, wx_id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.setting = CanvasSetting()
        self.currentProcessingItem = None
        self.nodes = {}
        self.srcNode = None
        self.srcPort = None
        self.tmpWire = None
        self.lastPnt = wx.Point(0, 0)
        # ui initial setting
        self.maxWidth = CANVAS_MAX_W
        self.maxHeight = CANVAS_MAX_H
        self.canvasToolbarMode = EnumCanvasToolbarMode.POINTER
        # self.SetVirtualSize((self.maxWidth, self.maxHeight))
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
        # todo: all node scaled
        # self.update_virtual_size()

    def on_resize(self, evt):
        if self.has_style(EnumCanvasStyle.STYLE_GRADIENT_BACKGROUND):
            self.Refresh(False)
        evt.Skip()

    def on_mouse_wheel(self, evt: wx.MouseEvent):
        if evt.ControlDown():
            _scale = self.setting.mFScale
            _scale += evt.GetWheelRotation() / (evt.GetWheelDelta() * 10)
            if _scale < self.setting.mFMinScale: _scale = self.setting.mFMinScale
            if _scale > self.setting.mFMaxScale: _scale = self.setting.mFMaxScale
            self.set_scale(_scale)
            self.Refresh(False)

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
        return wx.Point(pt[0] + (_x_view * _x_delta), pt[1] + (_y_view * _y_delta))

    def offset_rect(self, rect):
        _x_view, _y_view = self.GetViewStart()
        _x_delta, _y_delta = self.GetScrollPixelsPerUnit()
        rect.Offset(-(_x_view * _x_delta), -(_y_view * _y_delta))

    def add_item(self, item: BaseNodeShape):
        _nid = item.get_id()
        self.pdc.SetId(_nid)
        item.draw(self.pdc)
        self.pdc.SetIdBounds(_nid, item.get_bounding_box())
        self.nodes[_nid] = item

    def on_left_down(self, evt):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        _mode = self.canvasToolbarMode
        if _mode == EnumCanvasToolbarMode.POINTER:
            pass
        elif _mode == EnumCanvasToolbarMode.CONNECTION:
            self.srcNode = self.HitTest(_win_pt)
            if self.srcNode is not None:
                self.srcPort = self.srcNode.HitTest(_win_pt.x, _win_pt.y)
                if self.srcPort is not None:
                    self.srcPort.Disconnect()
                    self.tmpWire = WireShape(self.srcNode.GetRect().GetPosition() + self.srcPort.GetPosition(), _pt,
                                             self.srcPort.GetType())
            self.lastPnt = _pt
        else:
            if _mode == EnumCanvasToolbarMode.STATE:
                self.currentProcessingItem = StateNodeShape(self, size=wx.Size(100, 50), pos=_win_pt)
            elif _mode == EnumCanvasToolbarMode.SUB_STATE:
                pass
            elif _mode == EnumCanvasToolbarMode.INIT_STATE:
                pass
            elif _mode == EnumCanvasToolbarMode.FINAL_STATE:
                pass
        evt.Skip()

    def on_motion(self, evt):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        _mode = self.canvasToolbarMode
        if _mode == EnumCanvasToolbarMode.POINTER:
            # handle hover event
            _hit_item = self.HitTest(_win_pt)
            if _hit_item:
                _id = _hit_item.get_id()
                if _id in self.nodes and not _hit_item.isMouseOvered:
                    _hit_item.isMouseOvered = True
                    _hit_item.draw(self.pdc)
                    _rect = self.pdc.GetIdBounds(_id)
                    self.offset_rect(_rect)
                    self.RefreshRect(_rect, False)
            else:
                for k, v in self.nodes.items():
                    if v.isMouseOvered:
                        v.isMouseOvered = False
                        v.draw(self.pdc)
                        _rect = self.pdc.GetIdBounds(v.get_id())
                        self.offset_rect(_rect)
                        self.RefreshRect(_rect, False)
        if not evt.LeftIsDown() or self.srcNode is None:
            return
        if self.srcPort is None:
            _d_pt = _pt - self.lastPnt
            _rect = self.pdc.GetIdBounds(self.srcNode.GetId())
            self.pdc.TranslateId(self.srcNode.GetId(), _d_pt[0], _d_pt[1])
            _rect_2 = self.pdc.GetIdBounds(self.srcNode.GetId())
            _rect = _rect.Union(_rect_2)
            self.offset_rect(_rect)
            self.RefreshRect(_rect, False)
            self.lastPnt = _pt
            self.srcNode.SetRect(_rect_2)

            # Redraw wires
            for port in self.srcNode.GetPorts():
                for wire in port.GetWires():
                    _pt1 = wire.srcNode.GetRect().GetPosition() + wire.srcPort.GetPosition()
                    _pt2 = wire.dstNode.GetRect().GetPosition() + wire.dstPort.GetPosition()
                    self.draw_wire(wire, _pt1, _pt2)

        elif self.tmpWire is not None:
            self.draw_wire(self.tmpWire, pnt2=_win_pt)
        evt.Skip()

    def on_left_up(self, evt):
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        if self.canvasToolbarMode in [EnumCanvasToolbarMode.STATE,
                                      EnumCanvasToolbarMode.SUB_STATE,
                                      EnumCanvasToolbarMode.INIT_STATE,
                                      EnumCanvasToolbarMode.FINAL_STATE]:
            if self.currentProcessingItem is not None:
                self.currentProcessingItem.set_position(_win_pt)
                self.add_item(self.currentProcessingItem)
                self.Refresh(False)
        # Attempt to make a connection.
        if self.srcNode is not None:
            _dst_node = self.HitTest(_win_pt)
            if _dst_node is not None:
                _dst_port = _dst_node.HitTest(_win_pt.x, _win_pt.y)
                if _dst_port is not None and self.srcPort.GetType() != _dst_port.GetType() and self.srcNode.GetId() != _dst_port.GetId():
                    self.srcPort.Connect(_dst_port)

        # Erase the temp wire.
        if self.tmpWire is not None:
            _rect = self.pdc.GetIdBounds(self.tmpWire.GetId())
            self.pdc.RemoveId(self.tmpWire.GetId())
            self.offset_rect(_rect)
            self.RefreshRect(_rect, False)

        self.srcNode = None
        self.srcPort = None
        self.tmpWire = None
        evt.Skip()

    def HitTest(self, pt):
        _idxs = self.pdc.FindObjects(pt[0], pt[1], CANVAS_HIT_RADIUS)
        _hits = [idx for idx in _idxs if idx in self.nodes]
        return self.nodes[_hits[0]] if _hits else None

    def on_paint(self, event):
        _t1 = time.time()
        # Create a buffered paint DC.  It will create the real wx.PaintDC and
        # then blit the bitmap to it when dc is deleted.
        _dc = wx.BufferedPaintDC(self)
        if self.setting.mGCDCEnabled:
            _dc = wx.GCDC(_dc)

        # Use PrepareDC to set position correctly.
        self.PrepareDC(_dc)

        # draw the background
        self.draw_background(_dc)

        # Create a clipping rect from our position and size and the Update Region.
        _xv, _yv = self.GetViewStart()
        _dx, _dy = self.GetScrollPixelsPerUnit()
        _x, _y = (_xv * _dx, _yv * _dy)
        _rgn = self.GetUpdateRegion()
        _rgn.Offset(_x, _y)
        _rect = _rgn.GetBox()

        # Draw to the dc using the calculated clipping rect.
        self.pdc.DrawToDCClipped(_dc, _rect)
        print('repaint %.2F ms' % ((time.time() - _t1) * 100))

    def draw_background(self, dc):
        # erase the background
        if self.has_style(EnumCanvasStyle.STYLE_GRADIENT_BACKGROUND):
            _bk_size = self.GetVirtualSize() + wx.Size(self.setting.mGridSize.x, self.setting.mGridSize.y)
            if self.setting.mFScale != 1.0:
                dc.GradientFillLinear(wx.Rect(wx.Point(0, 0),
                                              wx.Size(_bk_size.x / self.setting.mFScale,
                                                      _bk_size.y / self.setting.mFScale)),
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

    def draw_wire(self, wire, pnt1=None, pnt2=None):
        rect1 = wire.GetRect()
        if pnt1 is not None:
            wire.pnt1 = pnt1
        if pnt2 is not None:
            wire.pnt2 = pnt2
        rect2 = wire.GetRect()
        rect = rect1.Union(rect2)
        self.offset_rect(rect)

        self.pdc.ClearId(wire.GetId())
        wire.Draw(self.pdc)
        self.RefreshRect(rect, False)

    def Load(self, filePath):
        with open(filePath, 'r') as f:
            data = json.load(f)
            for nodeData in data:
                props = nodeData['properties']
                node = self.append_node(
                    props['name'],
                    wx.Point(props['x'], props['y']),
                    nodeData['ins'].keys(),
                    nodeData['outs'].keys(),
                    props['color']
                )

    def get_node_port(self, node, port):
        return node.GetPorts(port)
