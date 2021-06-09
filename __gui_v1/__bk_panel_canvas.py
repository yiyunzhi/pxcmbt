import wx
import wx.adv
import wx.lib.agw.aui as aui
import json
from __gui_v1.define_gui import *
from application.define import EnumPanelRole
from application.wire import Wire
from application.node import Node


# todo: canvas scale, selection, selected
# todo: scroll, middlekey move


class CanvasSetting:
    def __init__(self):
        self.mFScale = 1.0
        self.mFMinScale = 0.3
        self.mFMaxScale = 3.0


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
        self.Bind(wx.EVT_TOOL, lambda evt: self.canvas.on_canvas_tool_changed(evt, EnumCanvasToolbarMode.NOTE),
                  _tb_note)
        _tb.ToggleTool(_tb_pointer, True)
        self.on_tool_changed(None, EnumCanvasToolbarMode.POINTER)
        return _tb

    def _bind_event(self):
        pass

    def on_tool_changed(self, evt, flag):
        print('--->on_tool_changed')
        self.canvas.set_canvas_toolbar_mode(flag)


class Canvas(wx.ScrolledWindow):
    def __init__(self, parent, wx_id, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, wx_id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.setting = CanvasSetting()
        self.nodes = {}
        self.srcNode = None
        self.srcPort = None
        self.tmpWire = None
        self.lastPnt = wx.Point(0, 0)
        # ui initial setting
        self.maxWidth = CANVAS_MAX_W
        self.maxHeight = CANVAS_MAX_H
        self.canvasToolbarMode = EnumCanvasToolbarMode.POINTER
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20, 20)
        # better ui
        # self.SetScrollbars(5, 5, 100, 100)
        self.SetBackgroundColour(wx.LIGHT_GREY)
        # self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        # self.SetDoubleBuffered(True)
        # create a PseudoDC to record our drawing
        self.pdc = wx.adv.PseudoDC()
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

    def get_canvas_toolbar_mode(self):
        return self.canvasToolbarMode

    def set_canvas_toolbar_mode(self, mode: EnumCanvasToolbarMode):
        self.canvasToolbarMode = mode

    def on_canvas_tool_changed(self, evt, flag):
        print('canvas toolbar changed', evt, flag)

    def set_scale(self, scale):
        if scale != 0:
            self.setting.mFScale = scale
        else:
            self.setting.mFScale = 1
        # todo: all node scaled
        # self.update_virtual_size()

    def on_mouse_wheel(self, evt: wx.MouseEvent):
        if evt.ControlDown():
            _scale = self.setting.mFScale
            _scale += evt.GetWheelRotation() / (evt.GetWheelDelta() * 10)
            if _scale < self.setting.mFMinScale: _scale = self.setting.mFMinScale
            if _scale > self.setting.mFMaxScale: _scale = self.setting.mFMaxScale
            self.set_scale(_scale)
            self.Refresh(False)

        evt.Skip()

    def on_key_down(self, evt):
        evt.Skip()

    def on_key_up(self, evt):
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

    def append_node(self, label, pos, ins, outs, colour=None):
        _node = Node(self, label, colour, rect=wx.Rect(pos.x, pos.y, 150, 100), ins=ins, outs=outs)
        _n_id = _node.GetId()
        self.pdc.SetId(_n_id)
        _node.draw(self.pdc)
        self.pdc.SetIdBounds(_n_id, _node.GetRect())
        self.nodes[_n_id] = _node
        return _node

    def on_left_down(self, evt):
        print('left down', self.HasFocus())
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
        self.srcNode = self.HitTest(_win_pt)
        if self.srcNode is not None:
            self.srcPort = self.srcNode.HitTest(_win_pt.x, _win_pt.y)
            if self.srcPort is not None:
                self.srcPort.Disconnect()
                self.tmpWire = Wire(self.srcNode.GetRect().GetPosition() + self.srcPort.GetPosition(), _pt,
                                    self.srcPort.GetType())
        self.lastPnt = _pt
        evt.Skip()

    def on_motion(self, evt):
        if not evt.LeftIsDown() or self.srcNode is None:
            return
        _pt = evt.GetPosition()
        _win_pt = self.convert_coords(_pt)
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
        # Attempt to make a connection.
        if self.srcNode is not None:
            _pt = evt.GetPosition()
            _win_pt = self.convert_coords(_pt)
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
        hits = [idx for idx in _idxs if idx in self.nodes]
        return self.nodes[hits[0]] if hits else None

    def on_paint(self, event):
        # Create a buffered paint DC.  It will create the real wx.PaintDC and
        # then blit the bitmap to it when dc is deleted.
        _dc = wx.BufferedPaintDC(self)
        _dc = wx.GCDC(_dc)

        # Use PrepateDC to set position correctly.
        self.PrepareDC(_dc)

        # We need to clear the dc BEFORE calling PrepareDC.
        _bg = wx.Brush(self.GetBackgroundColour())
        _dc.SetBackground(_bg)
        _dc.Clear()

        # Create a clipping rect from our position and size and the Update
        # Region.
        _xv, _yv = self.GetViewStart()
        _dx, _dy = self.GetScrollPixelsPerUnit()
        x, y = (_xv * _dx, _yv * _dy)
        _rgn = self.GetUpdateRegion()
        _rgn.Offset(x, y)
        _rect = _rgn.GetBox()

        # Draw to the dc using the calculated clipping rect.
        self.pdc.DrawToDCClipped(_dc, _rect)

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
