import os
import wx
from wx.lib.agw import aui
from wx.lib.floatcanvas import FloatCanvas
from wx.lib.floatcanvas.FCObjects import DrawObject
from application.define import *
from .define_gui import *
from .shape_note_node import NoteNodeShape
from .shape_state_node import StateNodeShape, InitStateNodeShape, FinalStateNodeShape
from .shape_wire import WireShape
from .canvas_gcdc import GCDCCanvas


class NodePlaceModifier:
    def __init__(self, canvas_mode):
        self.mode = canvas_mode

    def place(self, pos):
        if self.mode == EnumCanvasToolbarMode.NOTE:
            _notes_text = """this is a note component,
you can edit its content.
..."""
            _item = NoteNodeShape(pos, _notes_text)
        elif self.mode == EnumCanvasToolbarMode.STATE:
            _item = StateNodeShape(pos, 'Untitled State')
        elif self.mode == EnumCanvasToolbarMode.SUB_STATE:
            _item = None
        elif self.mode == EnumCanvasToolbarMode.CONNECTION:
            _item = None
        elif self.mode == EnumCanvasToolbarMode.FINAL_STATE:
            _item = FinalStateNodeShape(pos)
        elif self.mode == EnumCanvasToolbarMode.INIT_STATE:
            _item = InitStateNodeShape(pos)
        else:
            _item = None
        return _item


class CanvasRepositionModifier:
    def __init__(self, item, org_pos):
        self.item = item
        self.orgPos = org_pos
        self.curPos = org_pos
        self.mouseOffset = wx.Point(0, 0)
        self.inWires = None
        self.outWires = None

    def update_position(self, pos):
        self.orgPos = self.curPos
        self.curPos = pos

    def get_position_diff(self, reverse=False):
        if reverse:
            return self.orgPos - self.curPos
        return self.curPos - self.orgPos


class CanvasConnectionModifier:
    def __init__(self, src_node):
        self.srcNode = src_node
        self.dstNode = None
        self.srcPort = None
        self.dstPort = None
        self.wire = None


class CanvasSetting:
    def __init__(self):
        self.mDebug = True
        self.mMode = 0
        self.mFScale = 1.0
        self.mFMinScale = 0.4
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
    def __init__(self, parent, wx_id):
        wx.Panel.__init__(self, parent, wx_id)
        self.uuid = None
        self.role = EnumPanelRole.STATE_CHART_CANVAS
        self.canvasSetting = CanvasSetting()
        """
        classnames = ["Circle", "Ellipse", "Arc", "Rectangle", "ScaledText", "Polygon",
                  "Line", "Text", "PointSet","Point", "Arrow", "ArrowLine", "ScaledTextBox",
                  "SquarePoint","Bitmap", "ScaledBitmap", "Spline", "Group"]
        those class name could be used, since those are dynamic bound to the object
        etc.
            self.canvas.AddCircle...
        """
        # self.canvas = FloatCanvas.FloatCanvas(self, wx.ID_ANY, Debug=self.canvasSetting.mDebug)
        self.canvas = GCDCCanvas(self, wx.ID_ANY, debug=self.canvasSetting.mDebug)
        self.canvas.MaxScale = self.canvasSetting.mFMaxScale
        self.canvas.MINScale = self.canvasSetting.mFMinScale
        # member variable
        #self.scaleTimer = wx.PyTimer(self.on_scale_timer)
        self.nodePlaceModifier = None
        self.nodeRepositionModifier = None
        self.nodeConnectionModifier = None
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.toolbarIconSize = wx.Size(16, 16)
        self.canvasToolbar = self._create_toolbar()
        self.canvasStatusbar = self._create_statusbar()
        self.mainSizer.Add(self.canvasToolbar, 0, wx.EXPAND)
        self.mainSizer.Add(self.canvas, 1, wx.EXPAND)
        self.mainSizer.Add(self.canvasStatusbar, 0, wx.EXPAND)
        self._bind_event()
        self.SetSizer(self.mainSizer)
        self.Layout()

    def _create_statusbar(self):
        _sb = wx.StatusBar(self, wx.ID_ANY, style=0)
        _sb.SetSize(-1, 18)
        _sb.SetTransparent(0.8)
        _sb.SetFieldsCount(3, [72, -1, -1])
        # _sb_font = wx.Font(wx.SYS_DEFAULT_GUI_FONT)
        # _sb_font.SetPointSize(10)
        # _sb.SetFont(_sb_font)
        _sb.SetStatusText('Scale:%.2F' % self.canvasSetting.mFScale, 0)
        return _sb

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
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.canvas.Bind(FloatCanvas.EVT_MOTION, self.on_motion_canvas)
        self.canvas.Bind(FloatCanvas.EVT_MOUSEWHEEL, self.on_mouse_wheel_canvas)
        self.canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.on_mouse_left_down_canvas)
        self.canvas.Bind(FloatCanvas.EVT_LEFT_UP, self.on_mouse_left_up_canvas)
        self.canvas.Bind(FloatCanvas.EVT_MIDDLE_DOWN, self.on_mouse_middle_down_canvas)
        self.canvas.Bind(FloatCanvas.EVT_MIDDLE_UP, self.on_mouse_middle_up_canvas)
        self.canvas.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def _unbind_all_mouse_events(self):
        self.canvas.Unbind(FloatCanvas.EVT_MOTION)
        self.canvas.Unbind(FloatCanvas.EVT_MOUSEWHEEL)
        self.canvas.Unbind(FloatCanvas.EVT_LEFT_DOWN)
        self.canvas.Unbind(FloatCanvas.EVT_LEFT_UP)
        self.canvas.Unbind(FloatCanvas.EVT_MIDDLE_DOWN)
        self.canvas.Unbind(FloatCanvas.EVT_MIDDLE_UP)

    def update_scale_info_test(self):
        self.canvasStatusbar.SetStatusText('Scale:%.2F' % self.canvasSetting.mFScale, 0)

    def on_tool_changed(self, evt, flag):
        self.canvasSetting.mMode = flag

    def on_key_down(self, evt: wx.KeyEvent):
        _k_code = evt.GetKeyCode()
        self.process_key_down(_k_code)

    def process_key_down(self, k_code):
        if k_code == wx.WXK_ESCAPE:
            _tool = self.canvasToolbar.FindToolByIndex(EnumCanvasToolbarMode.POINTER)
            if _tool is not None:
                self.canvasToolbar.ToggleTool(_tool.GetId(), True)
                self.on_tool_changed(None, EnumCanvasToolbarMode.POINTER)
                self.canvasToolbar.Refresh()

    def add_item(self, item):
        if item is None:
            return
        _obj = self.canvas.AddObject(item)
        _obj.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.on_left_down_item)
        _obj.Bind(FloatCanvas.EVT_FC_LEFT_UP, self.on_left_up_item)
        _obj.Bind(FloatCanvas.EVT_FC_ENTER_OBJECT, self.on_enter_item)
        _obj.Bind(FloatCanvas.EVT_FC_LEAVE_OBJECT, self.on_leave_item)
        self.canvas.Draw()

    def remove_item(self, item):
        if isinstance(item, DrawObject):
            self.canvas.RemoveObject(item)
            # item.UnBindAll()

    def on_left_down_item(self, item):
        # print('on_item_left_down', item, item.HitCoordsPixel, item.HitCoords)
        item.on_left_down()
        # self.leftDownItem = item
        # handle reposition
        _mode = self.canvasSetting.mMode
        if not isinstance(item, WireShape):
            if _mode == EnumCanvasToolbarMode.POINTER:
                self.nodeRepositionModifier = CanvasRepositionModifier(item, item.HitCoords)
            elif _mode == EnumCanvasToolbarMode.CONNECTION:
                _conn_style = item.get_connection_style()
                if _conn_style == EnumShapeConnectionStyle.ANYWHERE:
                    self.nodeConnectionModifier = CanvasConnectionModifier(item)
                    self.nodeConnectionModifier.wire = WireShape(item.HitCoords, item.HitCoords)
                    self.nodeConnectionModifier.wire.set_line_style('ShortDash')
                    self.add_item(self.nodeConnectionModifier.wire)

    def on_left_up_item(self, item):
        print('on_item_left_down', item, item.HitCoordsPixel, item.HitCoords)
        item.on_left_up()
        if self.nodeRepositionModifier is not None:
            self.nodeRepositionModifier = None
        if self.nodeConnectionModifier is not None:
            self.remove_item(self.nodeConnectionModifier.wire)
            self.nodeConnectionModifier = None
            self.canvas.Draw(True)

    def on_enter_item(self, item):
        print('on_enter_item', item, item.HitCoordsPixel, item.HitCoords)
        item.on_enter()
        if self.nodeConnectionModifier is not None:
            self.nodeConnectionModifier.dstNode = item

    def on_leave_item(self, item):
        print('on_leave_item', item, item.HitCoordsPixel, item.HitCoords)
        item.on_leave()

    def on_motion_canvas(self, evt):
        _pos = evt.GetPosition()
        _world_pos = self.canvas.PixelToWorld(_pos)
        if self.nodeRepositionModifier is not None:
            self.nodeRepositionModifier.update_position(_world_pos)
            _item = self.nodeRepositionModifier.item
            _item.Move(self.nodeRepositionModifier.get_position_diff())
            self.canvas.Draw(True)
        if self.nodeConnectionModifier is not None:
            self.nodeConnectionModifier.wire.set_dst_point(_world_pos)
            self.canvas.Draw(True)
        evt.Skip()

    # def on_scale_timer(self):
    #     self.update_scale_info_test()
    #     self.canvas.Zoom(self.canvasSetting.mFScale)

    def on_mouse_wheel_canvas(self, evt: wx.MouseEvent):
        # print('on_mouse_wheel_canvas', evt)
        # _rot = evt.GetWheelRotation()
        # _rot = _rot / abs(_rot) * 0.1
        _scale = self.canvasSetting.mFScale
        _scale += evt.GetWheelRotation() / (evt.GetWheelDelta() * 10)
        if evt.ControlDown():  # move left-right
            if _scale < self.canvasSetting.mFMinScale: _scale = self.canvasSetting.mFMinScale
            if _scale > self.canvasSetting.mFMaxScale: _scale = self.canvasSetting.mFMaxScale
            # self.canvas.MoveImage((_rot, 0), 'Panel')
            self.update_scale_info_test()
            self.canvas.Zoom(_scale/self.canvasSetting.mFScale)
            self.canvasSetting.mFScale = _scale
        # else:  # move up-down
        #    self.canvas.MoveImage((0, _rot), 'Panel')
        evt.Skip()

    def on_mouse_left_down_canvas(self, evt: wx.MouseEvent):
        # todo: while place should call dialog, the name to given
        print('mouse left down canvas')
        _pos = evt.GetPosition()
        _world_pos = self.canvas.PixelToWorld(_pos)
        if self.canvasSetting.mMode != EnumCanvasToolbarMode.POINTER:
            self.nodePlaceModifier = NodePlaceModifier(self.canvasSetting.mMode)
        else:
            pass
        evt.Skip()

    def on_mouse_left_up_canvas(self, evt):
        _pos = evt.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.PixelToWorld(_pos))
        if self.nodePlaceModifier is not None:
            _item = self.nodePlaceModifier.place(_world_pos)
            if _item is not None:
                self.add_item(_item)
            self.nodePlaceModifier = None
        if self.nodeRepositionModifier is not None:
            self.nodeRepositionModifier = None
        if self.nodeConnectionModifier is not None:
            self.remove_item(self.nodeConnectionModifier.wire)
            self.nodeConnectionModifier = None
            self.canvas.Draw(True)
        evt.Skip()

    def on_mouse_middle_down_canvas(self, evt):
        # todo: start pan mode to drag the canvas
        print('on_mouse_middle_down_canvas', evt)
        evt.Skip()

    def on_mouse_middle_up_canvas(self, evt):
        print('on_mouse_middle_up_canvas', evt)
        evt.Skip()

    def on_save_as_png(self, event=None):
        _dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard="*.png", style=wx.FD_SAVE
        )
        if _dlg.ShowModal() == wx.ID_OK:
            _path = _dlg.GetPath()
            if not (_path[-4:].lower() == ".png"):
                _path = _path + ".png"
            self.canvas.SaveAsImage(_path)

    def zoom_to_fit(self, event):
        self.canvas.ZoomToBB()

    def clear(self, event=None):
        self._unbind_all_mouse_events()
        self.canvas.InitAll()
        self.canvas.Draw()

    def on_paint(self, evt: wx.PaintEvent):
        pass
