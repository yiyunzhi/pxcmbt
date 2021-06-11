import os
import wx
from wx.lib.agw import aui
from wxgraph import WxGEvent, DrawObject
from application.define import *
from .define_gui import *
from .shape_wire import WireShape
from wxgraph.wxcanvas import WxCanvas
from wxgraph.draw_graph_dotgrid import DrawGraphDotGrid
from .gui_mode import GUIModeMouse, GUIModeConnection, GUIModePlace


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
        self.mGridSize: wx.Size = wx.Size(50, 50)
        self.mGridLineMult: int = 5
        self.mGridColor: wx.Colour = wx.Colour(200, 200, 200)
        self.mGridStyle: int = wx.SHORT_DASH
        self.mShadowOffset: wx.RealPoint = wx.RealPoint(4, 4)
        self.mShadowFill: wx.Brush = wx.Brush(wx.Colour(150, 150, 150, 128), wx.BRUSHSTYLE_SOLID)
        # self.mLstAcceptedShapes = list()
        # self.mIPrintHAlign: int = EnumHAlign.halignCENTER
        # self.mIPrintVAlign: int = EnumVAlign.valignMIDDLE
        # self.mIPrintMode: int = EnumPrintMode.prnFIT_TO_MARGINS

class DemoCanvas(wx.Panel):
    def __init__(self, parent, wx_id=-1):
        super(DemoCanvas, self).__init__(parent, -1)

class StateChartCanvasViewPanel2(wx.Panel):
    def __init__(self, parent, wx_id):
        super(StateChartCanvasViewPanel2, self).__init__(parent, -1)
        self.uuid = None
        self.role = EnumPanelRole.STATE_CHART_CANVAS
        self.canvasSetting = CanvasSetting()
        self._canvasGrid = DrawGraphDotGrid(self.canvasSetting.mGridSize, size=1)
        self.canvas = DemoCanvas(self)
        # self.canvas.maxScale = self.canvasSetting.mFMaxScale
        # self.canvas.minScale = self.canvasSetting.mFMinScale
        # self.canvas.gridUnder = self._canvasGrid
        # self.canvas.set_mode(GUIModeMouse(self.canvas))
        # member variable
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.toolbarIconSize = wx.Size(16, 16)
        # self.canvasToolbar = self._create_toolbar()
        # self.canvasStatusbar = self._create_statusbar()
        # self.mainSizer.Add(self.canvasToolbar, 0, wx.EXPAND)
        self.mainSizer.Add(self.canvas, 1, wx.EXPAND)
        # self.mainSizer.Add(self.canvasStatusbar, 0, wx.EXPAND)
        self._bind_event()
        self.SetSizer(self.mainSizer)
        self.Layout()

    def _bind_event(self):
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def on_key_down(self, evt):
        print('on_key_down', evt)


class StateChartCanvasViewPanel(wx.Panel):
    def __init__(self, parent, wx_id):
        wx.Panel.__init__(self, parent, wx_id)
        self.uuid = None
        self.role = EnumPanelRole.STATE_CHART_CANVAS
        self.canvasSetting = CanvasSetting()
        """
        wxCanvas supply the below shortcut method to add a shape.
        classnames = ["Circle", "Ellipse", "Arc", "Rectangle", "ScaledText", "Polygon",
                  "Line", "Text", "PointSet","Point", "Arrow", "ArrowLine", "ScaledTextBox",
                  "SquarePoint","Bitmap", "ScaledBitmap", "Spline", "Group"]
        those class name could be used, since those are dynamic bound to the object
        etc.
            self.canvas.AddCircle...
        """
        self._canvasGrid = DrawGraphDotGrid(self.canvasSetting.mGridSize, size=1)
        self.canvas = WxCanvas(self, wx.ID_ANY, debug=self.canvasSetting.mDebug)
        self.canvas.maxScale = self.canvasSetting.mFMaxScale
        self.canvas.minScale = self.canvasSetting.mFMinScale
        self.canvas.gridUnder = self._canvasGrid
        self.canvas.set_mode(GUIModeMouse(self.canvas))
        # member variable
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
        _sb.SetStatusText('scale:%.2F' % self.canvasSetting.mFScale, 0)
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
        self.Bind(WxGEvent.EVT_MOTION, self.on_motion_view)
        self.Bind(WxGEvent.EVT_MOUSEWHEEL, self.on_mouse_wheel_view)
        self.Bind(WxGEvent.EVT_LEFT_DOWN, self.on_mouse_left_down_view)
        self.Bind(WxGEvent.EVT_LEFT_UP, self.on_mouse_left_up_view)
        self.Bind(WxGEvent.EVT_MIDDLE_DOWN, self.on_mouse_middle_down_view)
        self.Bind(WxGEvent.EVT_MIDDLE_UP, self.on_mouse_middle_up_view)
        self.Bind(WxGEvent.EVT_LEFT_DCLICK, self.on_item_double_click)
        self.Bind(WxGEvent.EVT_SCALE_CHANGED, self.on_canvas_scale_changed)
        # self.Bind(wx.EVT_KEY_DOWN, self.on_key_down_view)
        # use EVT_CHAR_HOOK replace EVT_KEY_DOWN, if use panel in a panel
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down_view)

    def _unbind_all_mouse_events(self):
        self.Unbind(WxGEvent.EVT_MOTION)
        self.Unbind(WxGEvent.EVT_MOUSEWHEEL)
        self.Unbind(WxGEvent.EVT_LEFT_DOWN)
        self.Unbind(WxGEvent.EVT_LEFT_UP)
        self.Unbind(WxGEvent.EVT_MIDDLE_DOWN)
        self.Unbind(WxGEvent.EVT_MIDDLE_UP)
        self.Unbind(WxGEvent.EVT_SCALE_CHANGED)

    def update_scale_info_test(self):
        self.canvasStatusbar.SetStatusText('scale:%.2F' % self.canvasSetting.mFScale, 0)

    def on_tool_changed(self, evt, flag):
        self.canvasSetting.mMode = flag
        if flag in [EnumCanvasToolbarMode.STATE,
                    EnumCanvasToolbarMode.SUB_STATE,
                    EnumCanvasToolbarMode.INIT_STATE,
                    EnumCanvasToolbarMode.FINAL_STATE,
                    EnumCanvasToolbarMode.NOTE]:
            if self.canvas.GUIMode is None or not isinstance(self.canvas.GUIMode, GUIModePlace):
                self.canvas.set_mode(GUIModePlace(flag))
            self.canvas.GUIMode.set_shape_type(flag)
        elif flag == EnumCanvasToolbarMode.POINTER:
            if self.canvas.GUIMode is None or not isinstance(self.canvas.GUIMode, GUIModeMouse):
                self.canvas.set_mode(GUIModeMouse())

    def on_canvas_scale_changed(self, event):
        self.canvasSetting.mFScale = event.get_scale()
        self.update_scale_info_test()

    def on_key_down_view(self, evt: wx.KeyEvent):
        print('on_key_down_view',evt.GetKeyCode())
        _k_code = evt.GetKeyCode()
        self.process_key_down(_k_code)
        evt.Skip()

    def on_key_up_view(self, evt):
        print('on_key_up_view')

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
        _obj = self.canvas.add_object(item)
        _obj.Bind(WxGEvent.EVT_FC_LEFT_DOWN, self.on_left_down_item)
        _obj.Bind(WxGEvent.EVT_FC_LEFT_UP, self.on_left_up_item)
        _obj.Bind(WxGEvent.EVT_FC_ENTER_OBJECT, self.on_enter_item)
        _obj.Bind(WxGEvent.EVT_FC_LEAVE_OBJECT, self.on_leave_item)
        self.canvas.draw()

    def remove_item(self, item):
        if isinstance(item, DrawObject):
            self.canvas.remove_object(item)
            # item.UnBindAll()

    def on_item_double_click(self, *args):
        print('on_item_double_click', *args)

    def on_left_down_item(self, item):
        print('on_item_left_down', item, item.hitCoordsPixel, item.hitCoords)
        #     elif _mode == EnumCanvasToolbarMode.CONNECTION:
        #         _conn_style = item.get_connection_style()
        #         if _conn_style == EnumShapeConnectionStyle.ANYWHERE:
        #             self.nodeConnectionModifier = CanvasConnectionModifier(item)
        #             self.nodeConnectionModifier.wire = WireShape(item.HitCoords, item.HitCoords)
        #             self.nodeConnectionModifier.wire.set_line_style('ShortDash')
        #             self.add_item(self.nodeConnectionModifier.wire)

    def on_left_up_item(self, item):
        print('on_item_left_up', item, item.hitCoordsPixel, item.hitCoords)
        # if self.nodeConnectionModifier is not None:
        #     self.remove_item(self.nodeConnectionModifier.wire)
        #     self.nodeConnectionModifier = None
        #     self.canvas.draw(True)

    def on_enter_item(self, item):
        print('on_enter_item', item, item.hitCoordsPixel, item.hitCoords)
        item.on_enter()

    def on_leave_item(self, item):
        print('on_leave_item', item, item.hitCoordsPixel, item.hitCoords)
        item.on_leave()

    def on_motion_view(self, evt):
        _pos = evt.GetPosition()
        _world_pos = self.canvas.pixel_to_world(_pos)
        # if self.nodeConnectionModifier is not None:
        #     self.nodeConnectionModifier.wire.set_dst_point(_world_pos)
        #     self.canvas.draw(True)
        evt.Skip()

    def on_mouse_wheel_view(self, evt: wx.MouseEvent):
        print('on_mouse_wheel_canvas', evt)
        evt.Skip()

    def on_mouse_left_down_view(self, evt: wx.MouseEvent):
        # todo: while place should show a dialog the name give to
        print('mouse left down view')
        _pos = evt.GetPosition()
        _world_pos = self.canvas.pixel_to_world(_pos)
        evt.Skip()

    def on_mouse_left_up_view(self, evt):
        _pos = evt.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        # if self.nodeConnectionModifier is not None:
        #     self.remove_item(self.nodeConnectionModifier.wire)
        #     self.nodeConnectionModifier = None
        #     self.canvas.draw(True)
        evt.Skip()

    def on_mouse_middle_down_view(self, evt):
        # todo: start pan mode to drag the canvas
        print('on_mouse_middle_down_view', evt)
        evt.Skip()

    def on_mouse_middle_up_view(self, evt):
        print('on_mouse_middle_up_view', evt)
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
            self.canvas.save_as_image(_path)

    def zoom_to_fit(self, event):
        self.canvas.zoom_to_bb()

    def clear(self, event=None):
        self._unbind_all_mouse_events()
        self.canvas.init_all()
        self.canvas.draw()
