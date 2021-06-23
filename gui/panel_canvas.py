from pubsub import pub
from wx.lib.agw import aui
from wxgraph import WxGEvent, DrawObject
from application.define import *
from .define_gui import *
from .shape_transition import TransitionWireShape
from .shape_state_node import StateChartNode, StateNodeShape
from .shape_note_node import NoteNodeShape
from application.utils_helper import util_get_uuid_string
from wxgraph import DrawObjectSquarePoint
from wxgraph.wxcanvas import WxCanvas
from wxgraph.draw_graph_dotgrid import DrawGraphDotGrid
from .gui_mode import GUIModeMouse, GUIModeConnection, GUIModePlace
from .menu_context_menu import GuiStateItemContextMenu


class CanvasSetting:
    def __init__(self):
        self.mDebug = True
        self.mMode = 0
        self.mFScale = 1.0
        self.mFMinScale = 0.4
        self.mFMaxScale = 4.0
        self.mStyle = EnumCanvasStyle.STYLE_DEFAULT
        # self.mBackgroundColor: wx.Colour = wx.Colour(240, 240, 240)
        # self.mCommonHoverColor: wx.Colour = wx.Colour(120, 120, 255)
        # self.mGradientFrom: wx.Colour = wx.Colour(240, 240, 240)
        # self.mGradientTo: wx.Colour = wx.Colour(200, 200, 255)
        self.mGridSize: wx.Size = wx.Size(50, 50)
        # self.mGridLineMult: int = 5
        # self.mGridColor: wx.Colour = wx.Colour(200, 200, 200)
        # self.mGridStyle: int = wx.SHORT_DASH
        # self.mShadowOffset: wx.RealPoint = wx.RealPoint(4, 4)
        # self.mShadowFill: wx.Brush = wx.Brush(wx.Colour(150, 150, 150, 128), wx.BRUSHSTYLE_SOLID)
        # self.mLstAcceptedShapes = list()
        # self.mIPrintHAlign: int = EnumHAlign.halignCENTER
        # self.mIPrintVAlign: int = EnumVAlign.valignMIDDLE
        # self.mIPrintMode: int = EnumPrintMode.prnFIT_TO_MARGINS

    def serialize(self):
        _d = {'mDebug': self.mDebug, 'mMode': self.mMode,
              'mFScale': self.mFScale, 'mFMinScale': self.mFMinScale,
              'mFMaxScale': self.mFMaxScale, 'mStyle': self.mStyle,
              'mGridSize': self.mGridSize}
        return _d

    def deserialize(self, data):
        for k, v in data:
            if hasattr(self, k):
                setattr(self, k, v)


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
        self.canvas.init_all()
        self.canvas.maxScale = self.canvasSetting.mFMaxScale
        self.canvas.minScale = self.canvasSetting.mFMinScale
        self.canvas.gridUnder = self._canvasGrid
        self.canvas.set_mode(GUIModeMouse(self.canvas))
        self._drawObjectCurrentConnPt = None
        self._lstCtrlPtDrawObjects = list()
        self._wires = dict()
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
        self.Bind(WxGEvent.EVT_RIGHT_DOWN, self.on_mouse_right_down_view)
        self.Bind(WxGEvent.EVT_RIGHT_UP, self.on_mouse_right_up_view)
        self.Bind(WxGEvent.EVT_MIDDLE_DOWN, self.on_mouse_middle_down_view)
        self.Bind(WxGEvent.EVT_MIDDLE_UP, self.on_mouse_middle_up_view)
        self.Bind(WxGEvent.EVT_LEFT_DCLICK, self.on_double_click_view)
        self.Bind(WxGEvent.EVT_SCALE_CHANGED, self.on_canvas_scale_changed)
        # self.Bind(wx.EVT_KEY_DOWN, self.on_key_down_view) not works
        # use EVT_CHAR_HOOK replace EVT_KEY_DOWN better, if use a panel in another panel
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down_view)
        pub.subscribe(self.on_node_item_delete_requested, EnumAppSignals.sigV2VGuiModeDelItemRequested)

    def _unbind_all_mouse_events(self):
        self.Unbind(WxGEvent.EVT_MOTION)
        self.Unbind(WxGEvent.EVT_MOUSEWHEEL)
        self.Unbind(WxGEvent.EVT_LEFT_DOWN)
        self.Unbind(WxGEvent.EVT_LEFT_UP)
        self.Unbind(WxGEvent.EVT_MIDDLE_DOWN)
        self.Unbind(WxGEvent.EVT_MIDDLE_UP)
        self.Unbind(WxGEvent.EVT_SCALE_CHANGED)

    def serialize(self):
        _d = dict()
        _d.update({'canvas': {'setting': self.canvasSetting.serialize()},
                   'nodes': list(),
                   'wires': list()})
        _objects = self.canvas.get_all_objects()
        for obj in _objects:
            if isinstance(obj, StateChartNode):
                _d['nodes'].append(obj.serialize())
            elif isinstance(obj, TransitionWireShape):
                _d['wires'].append(obj.serialize())
        return _d

    def deserialize(self, data):
        if hasattr(data, 'canvas'):
            _canvas = data['canvas']['setting']
        if hasattr(data, 'nodes'):
            _nodes = data['nodes']
            for x in _nodes:
                _cls = x['class']
                _role = x['role']
                _uuid = x['uuid']
                if _cls == 'StateNodeShape':
                    _conn_style = x['connectionStyle']
                    _is_visible = x['isVisible']
                    _name_text = x['nameText']
                    _position = x['position']
                    _node = StateNodeShape(_position, _name_text)
                    _node.isVisible = _is_visible
                    _node.connectionStyle = _conn_style
                    _node.update()

        if hasattr(data, 'wires'):
            _wires = data['wires']
            for x in _wires:
                pass

    def update_scale_info_test(self):
        self.canvasStatusbar.SetStatusText('scale:%.2F' % self.canvasSetting.mFScale, 0)

    def add_connection_pair(self, src_node, dst_node, src_pt, dst_pt):
        _wire = TransitionWireShape()
        _wire.uuid = util_get_uuid_string()
        _wire.srcNode = src_node
        _wire.dstNode = dst_node
        _wire.set_src_point(src_pt)
        _wire.set_dst_point(dst_pt)
        _wire.set_connection_valid_style()
        self.add_item(_wire)
        self._wires.update({_wire.uuid: _wire})
        _wire.srcNode.add_out_wire(_wire)
        _wire.dstNode.add_in_wire(_wire)
        self.canvas.draw()

    def update_connection_pair(self, wire_item, org_src_node, org_dst_node):
        if org_src_node is not wire_item.srcNode:
            org_src_node.remove_out_wire(wire_item)
            wire_item.srcNode.add_out_wire(wire_item)
        if org_dst_node is not wire_item.dstNode:
            org_dst_node.remove_in_wire(wire_item)
            wire_item.dstNode.add_in_wire(wire_item)

    def remove_connection_pair(self, wire, org_src_node, org_dst_node):
        self.remove_wire(wire)
        org_src_node.remove_out_wire(wire)
        org_dst_node.remove_in_wire(wire)
        self.canvas.draw(True)

    def remove_wire(self, wire):
        _uuid = wire.uuid
        if _uuid in self._wires:
            self._wires.pop(_uuid)
        self.remove_item(wire)

    def on_node_item_delete_requested(self, items):
        for x in items:
            # first remove the wires
            for wire in x.inWires:
                self.remove_wire(wire)
            for wire in x.outWires:
                self.remove_wire(wire)
            x.remove_in_wire()
            x.remove_out_wire()
            self.remove_item(x)
        self.canvas.draw(True)

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
        elif flag == EnumCanvasToolbarMode.CONNECTION:
            if self.canvas.GUIMode is None or not isinstance(self.canvas.GUIMode, GUIModeConnection):
                # if self._drawObjectConnPts not in self.canvas.get_fore_draw_list():
                #     self.canvas.add_object(self._drawObjectConnPts)
                self.canvas.set_mode(GUIModeConnection())
        pub.sendMessage(EnumAppSignals.sigV2VCanvasToolbarModeChanged, mode=flag)

    def on_canvas_scale_changed(self, event):
        self.canvasSetting.mFScale = event.get_scale()
        self.update_scale_info_test()

    def on_key_down_view(self, evt: wx.KeyEvent):
        _k_code = evt.GetKeyCode()
        if _k_code == wx.WXK_ESCAPE:
            self.reset_toolbar_mode()
        evt.Skip()

    def reset_toolbar_mode(self):
        _tool = self.canvasToolbar.FindToolByIndex(EnumCanvasToolbarMode.POINTER)
        if _tool is not None:
            self.canvasToolbar.ToggleTool(_tool.GetId(), True)
            self.on_tool_changed(None, EnumCanvasToolbarMode.POINTER)
            self.canvasToolbar.Refresh()

    def add_item(self, item):
        # todo: base on the item style determinne, if bind the event, set the mode...
        if item is None:
            return
        if item.uuid is None:
            item.uuid = util_get_uuid_string()
        _obj = self.canvas.add_object(item)
        _obj.bind(WxGEvent.EVT_FC_LEFT_DOWN, self.on_left_down_item)
        _obj.bind(WxGEvent.EVT_FC_LEFT_UP, self.on_left_up_item)
        _obj.bind(WxGEvent.EVT_FC_RIGHT_DOWN, self.on_right_down_item)
        _obj.bind(WxGEvent.EVT_FC_RIGHT_UP, self.on_right_up_item)
        _obj.bind(WxGEvent.EVT_FC_ENTER_OBJECT, self.on_enter_item)
        _obj.bind(WxGEvent.EVT_FC_LEAVE_OBJECT, self.on_leave_item)
        _obj.bind(WxGEvent.EVT_FC_LEFT_DCLICK, self.on_double_click_item)
        self.canvas.draw()
        return _obj

    def remove_item(self, item):
        if isinstance(item, DrawObject):
            if self.canvas.has_object(item):
                self.canvas.remove_object(item)
            # item.UnBindAll()

    def show_item_connect_points(self, item, state=True):
        if self._drawObjectCurrentConnPt is not None:
            if self.canvas.has_object(self._drawObjectCurrentConnPt):
                self.canvas.remove_object(self._drawObjectCurrentConnPt)
        self._drawObjectCurrentConnPt = item.get_connection_points_shape()
        if self._drawObjectCurrentConnPt is None:
            return
        if state:
            self.canvas.add_object(self._drawObjectCurrentConnPt)
        else:
            self.canvas.remove_object(self._drawObjectCurrentConnPt)

    def on_double_click_item(self, item):
        print('on_double_click_item', item, item.hitCoordsPixel, item.hitCoords)
        if isinstance(item, StateNodeShape):
            pub.sendMessage(EnumAppSignals.sigV2VCanvasNodeDClicked, uuid=self.uuid, role=self.role, item=item)
        elif isinstance(item, TransitionWireShape):
            pass
        elif isinstance(item, NoteNodeShape):
            pub.sendMessage(EnumAppSignals.sigV2VCanvasNodeNoteDClicked, uuid=self.uuid, role=self.role, item=item)

    def on_left_down_item(self, item):
        print('on_item_left_down', item, item.hitCoordsPixel, item.hitCoords)
        # todo: use has_style('hasProperties')
        pub.sendMessage(EnumAppSignals.sigV2VCanvasNodeShowProps, item=item)

    def on_left_up_item(self, item):
        print('on_item_left_up', item, item.hitCoordsPixel, item.hitCoords)

    def on_right_down_item(self, item):
        print('on_right_down_item', item, item.hitCoordsPixel, item.hitCoords)

    def on_right_up_item(self, item):
        print('on_item_right_up', item, item.hitCoordsPixel, item.hitCoords)
        _cm = GuiStateItemContextMenu(self)
        _cm.show()

    def on_cm_delete_item(self, event):
        print('delete item')

    def on_enter_item(self, item):
        print('on_enter_item', item, item.hitCoordsPixel, item.hitCoords)
        item.on_enter()
        _gui_mode = self.canvas.GUIMode
        if isinstance(_gui_mode, GUIModeConnection):
            if isinstance(item, StateChartNode):
                self.show_item_connect_points(item)

        elif isinstance(_gui_mode, GUIModeMouse):
            if isinstance(item, TransitionWireShape):
                _ctrls_pts = item.get_control_points()
                for pt in _ctrls_pts:
                    _draw_obj = DrawObjectSquarePoint(pt, size=TransitionWireShape.CTRL_PT_SIZE)
                    self._lstCtrlPtDrawObjects.append(self.canvas.add_object(_draw_obj))
            if _gui_mode.useMouseRewire and isinstance(item, StateChartNode):
                self.show_item_connect_points(item)
        self.canvas.draw(True)

    def on_leave_item(self, item):
        print('on_leave_item', item, item.hitCoordsPixel, item.hitCoords)
        item.on_leave()
        try:
            self.show_item_connect_points(item, False)
            self._drawObjectCurrentConnPt = None
        except:
            pass
        if self._lstCtrlPtDrawObjects:
            self.canvas.remove_objects(self._lstCtrlPtDrawObjects)
            self._lstCtrlPtDrawObjects.clear()
        self.canvas.draw(True)

    def on_motion_view(self, evt):
        _pos = evt.GetPosition()
        _world_pos = self.canvas.pixel_to_world(_pos)
        evt.Skip()

    def on_mouse_wheel_view(self, evt: wx.MouseEvent):
        print('on_mouse_wheel_canvas', evt)
        evt.Skip()

    def on_double_click_view(self, *args):
        print('on_double_click_view', *args)

    def on_mouse_left_down_view(self, evt: wx.MouseEvent):
        # todo: while place should show a dialog the name give to
        print('mouse left down view')
        _pos = evt.GetPosition()
        _world_pos = self.canvas.pixel_to_world(_pos)
        evt.Skip()

    def on_mouse_left_up_view(self, evt):
        _pos = evt.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        evt.Skip()

    def on_mouse_right_up_view(self, evt):
        pass

    def on_mouse_right_down_view(self, evt):
        pass

    def on_mouse_middle_down_view(self, evt):
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
