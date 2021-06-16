import numpy as N
from pubsub import pub
from wxgraph.gui_mode import GUIModeBase, GraphCursors
from wxgraph.events import *
from wxgraph import DrawObjectSquarePoint
import wxgraph.util_bbox as bbox
from .shape_state_node import StateNodeShape, FinalStateNodeShape, InitStateNodeShape, StateChartNode
from .shape_note_node import NoteNodeShape
from .shape_transition import TransitionWireShape, StateChartTransition
from .define_gui import *
from application.define import *


# some mix-ins for use with the other modes:
class GUIModeZoomWithMouseWheelMixin:
    def on_wheel(self, event: wx.MouseEvent):
        _scale = self.canvas.scale
        _scale += event.GetWheelRotation() / (event.GetWheelDelta() * 10)
        _pos = event.GetPosition()
        if event.ControlDown():
            if _scale < self.canvas.minScale: _scale = self.canvas.minScale
            if _scale > self.canvas.maxScale: _scale = self.canvas.maxScale
            self.canvas.zoom(_scale / self.canvas.scale, _pos, center_coords="Pixel", keep_point_in_place=True)
        super(GUIModeZoomWithMouseWheelMixin, self).on_wheel(event)


class GUIModePlace(GUIModeBase):
    def __init__(self, shape_type=None, canvas=None):
        GUIModeBase.__init__(self, canvas)
        self._shapeType = shape_type
        self._isShapeTypeReady = False

    def _add_item(self, item):
        _canvas_parent = self.canvas.GetParent()
        if item is None:
            return
        _obj = self.canvas.add_object(item)
        if _canvas_parent is not None:
            _obj.bind(EVT_FC_LEFT_DOWN, _canvas_parent.on_left_down_item)
            _obj.bind(EVT_FC_LEFT_UP, _canvas_parent.on_left_up_item)
            _obj.bind(EVT_FC_ENTER_OBJECT, _canvas_parent.on_enter_item)
            _obj.bind(EVT_FC_LEAVE_OBJECT, _canvas_parent.on_leave_item)
        self.canvas.draw()

    def set_shape_type(self, shape_type):
        self._shapeType = shape_type

    def on_left_down(self, event):
        self._isShapeTypeReady = self._shapeType is not None
        super(GUIModePlace, self).on_left_down(event)

    def on_left_up(self, event: wx.MouseEvent):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        if self._isShapeTypeReady:
            _item = None
            if self._shapeType == EnumCanvasToolbarMode.STATE:
                _item = StateNodeShape(_world_pos, 'Untitled State')
            elif self._shapeType == EnumCanvasToolbarMode.INIT_STATE:
                _item = InitStateNodeShape(_world_pos)
            elif self._shapeType == EnumCanvasToolbarMode.SUB_STATE:
                _item = None
            elif self._shapeType == EnumCanvasToolbarMode.FINAL_STATE:
                _item = FinalStateNodeShape(_world_pos)
            elif self._shapeType == EnumCanvasToolbarMode.NOTE:
                _str = "This is a note component.\nyou could add more text\n..."
                _item = NoteNodeShape(_world_pos, _str)
            if _item is not None:
                self._add_item(_item)
            self._isShapeTypeReady = False
        super(GUIModePlace, self).on_left_up(event)


class GUIModeConnection(GUIModeBase):
    def __init__(self, canvas=None):
        GUIModeBase.__init__(self, canvas)
        self.srcNode = None
        self.dstNode = None
        self.srcPort = None
        self.dstPort = None
        self.wire = None

    def on_left_down(self, event):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        _hit_object = self.canvas.objectUnderMouse
        _canvas_parent = self.canvas.GetParent()
        if _canvas_parent is not None:
            if _hit_object is not None and isinstance(_hit_object, StateChartNode):
                if _hit_object.get_connection_style() != EnumShapeConnectionStyle.NONE:
                    self.srcNode = _hit_object
                    _closest_pt, _uv = _hit_object.get_connection_point_at(_world_pos)
                    _wire = TransitionWireShape(_closest_pt, _closest_pt)
                    _wire.srcNode = _hit_object
                    self.wire = self.canvas.add_object(_wire)
                    self.wire.set_connection_invalid_style()
                    self.canvas.draw()
        super(GUIModeConnection, self).on_left_down(event)

    def on_left_up(self, event):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        _hit_object = self.canvas.objectUnderMouse
        _canvas_parent = self.canvas.GetParent()
        if _canvas_parent is not None:
            if _hit_object is not None and self.srcNode is not None and isinstance(_hit_object, StateChartNode):
                self.dstNode = _hit_object
                _closest_pt, _uv = _hit_object.get_connection_point_at(_world_pos)
                _canvas_parent.add_connection_pair(self.srcNode, self.dstNode, self.wire.srcPt, _closest_pt)
        if self.wire is not None:
            self.canvas.remove_object(self.wire)
            self.srcNode = None
            self.dstNode = None
            self.wire = None
            self.canvas.draw()
        super(GUIModeConnection, self).on_left_up(event)

    def on_motion(self, event):
        _pos = event.GetPosition()
        _world_pos = self.canvas.pixel_to_world(_pos)
        _hit_object = self.canvas.objectUnderMouse
        if self.wire is not None:
            if _hit_object is not None:
                self.wire.set_connection_valid_style()
            else:
                self.wire.set_connection_invalid_style()
            if self.srcNode is not None:
                self.wire.dstNode = _hit_object
                self.wire.set_dst_point(N.array(_world_pos, N.float))
            self.canvas.draw(True)

        super(GUIModeConnection, self).on_motion(event)


class GUIModeMouse(GUIModeZoomWithMouseWheelMixin, GUIModeBase):
    """

    Mouse mode checks for a hit test, and if nothing is hit,
    raises a FloatCanvas mouse event for each event.

    """

    # todo: multi item select and move
    # todo: multi item select with ctrl_key and rubberband
    def __init__(self, canvas=None):
        GUIModeBase.__init__(self, canvas)
        self.selectedItems = list()
        self.orgPos = None
        self.curPos = None
        # variable for wire and rewire
        self.useMouseRewire = False
        self.wireOrgSrcNode = None
        self.wireOrgDstNode = None
        # variable for pan
        self.panCursor = self.cursors.handCursor
        self.panGrabCursor = self.cursors.grabHandCursor
        self.panStartMove = None
        self.panMidMove = None
        self.panPrevMoveXY = None
        self.panEndMove = None
        self.panMoveTimer = wx.PyTimer(self.on_pan_move_timer)
        self.panRedrawDelayMs = 10
        # variable for rubber bandbox
        self.rbDrawRect = False
        self.rbStartPos = None
        self.rbRect = None
        # highlight items
        # bind the event
        pub.subscribe(self.on_canvas_mode_changed, EnumAppSignals.sigV2VCanvasToolbarModeChanged)

    def _update_position(self, pos):
        self.orgPos = self.curPos
        self.curPos = pos

    def _get_position_diff(self, reverse=False):
        if self.orgPos is None or self.curPos is None:
            return 0, 0
        if reverse:
            return self.orgPos - self.curPos
        return self.curPos - self.orgPos

    def _on_select_item(self, item):
        _ctrl_key_state = wx.GetKeyState(wx.WXK_CONTROL)
        #if item in self.selectedItems and item.isSelected:
        item.set_selected(not item.isSelected)
        if not item.isSelected and item in self.selectedItems:
            self.selectedItems.remove(item)
        elif item.isSelected and item not in self.selectedItems:
            self.selectedItems.append(item)
        if not _ctrl_key_state and item.isSelected:
            self._reset_selected_items_style(item)

    def _reset_selected_items_style(self, exclusive=None):
        for x in self.selectedItems:
            if exclusive is not None:
                if x is exclusive:
                    continue
            x.set_selected(False)

    def _on_rewire(self, item, pos_diff, object_at, current_pos):
        _len_ctrl_pt = item.get_control_points_length()
        if item.currentSelectedCtrlPtIdx == 0:
            _conn_pt = None
            if item.srcNode is not None:
                _conn_pt, _uv = item.srcNode.get_connection_point_at(current_pos)
                item.set_connection_valid_style()
            else:
                item.set_connection_invalid_style()
            if _conn_pt is None:
                # check if is connection broken
                item.srcNode = None
                if object_at is not None:
                    if object_at is not item.srcNode and isinstance(object_at, StateChartNode):
                        item.srcNode = object_at
                        item.set_src_point(current_pos)
            else:
                # still connectable
                item.set_src_point(_conn_pt)
        elif item.currentSelectedCtrlPtIdx == _len_ctrl_pt - 1:
            _conn_pt = None
            if item.dstNode is not None:
                _conn_pt, _uv = item.dstNode.get_connection_point_at(current_pos)
            else:
                item.set_connection_invalid_style()
            if _conn_pt is None:
                # check if is connection broken
                item.dstNode = None
                if object_at is not None:
                    if object_at is not item.dstNode and isinstance(object_at, StateChartNode):
                        item.dstNode = object_at
                        item.set_dst_point(current_pos)
            else:
                # still connectable
                item.set_dst_point(_conn_pt)
        item.move_control_point(pos_diff)

    def _on_draw_rubber_band(self, event):
        _x, _y = self.rbStartPos
        _corner_x, _corner_y = event.GetPosition()
        _w, _h = (_corner_x - _x, _corner_y - _y)
        if abs(_w) > 5 and abs(_h) > 5:
            # draw the RB box
            _dc = wx.ClientDC(self.canvas)
            _dc.SetPen(wx.Pen('#0ab', 1, wx.SHORT_DASH))
            _dc.SetBrush(wx.TRANSPARENT_BRUSH)
            _dc.SetLogicalFunction(wx.XOR)
            if self.rbRect:
                _dc.DrawRectangle(*self.rbRect)
            self.rbRect = ((_x, _y), (_w, _h))
            _dc.DrawRectangle(*self.rbRect)
        # self.canvas.raise_graph_event(event, EVT_FC_MOTION)

    def on_canvas_mode_changed(self, mode):
        self._reset_selected_items_style()

    def on_pan_move_timer(self):
        self.canvas.draw()

    # Handlers
    def on_left_down(self, event):
        _pos = event.GetPosition()
        _world_pos = self.canvas.pixel_to_world(_pos)
        _hit_object = self.canvas.objectUnderMouse
        _ctrl_key_state = wx.GetKeyState(wx.WXK_CONTROL)
        if _hit_object is not None:
            if _hit_object not in self.selectedItems:
                self._on_select_item(_hit_object)
            if isinstance(_hit_object, TransitionWireShape):
                _hit_object.guess_control_point(_world_pos)
                _len = _hit_object.get_control_points_length()
                self.wireOrgSrcNode = _hit_object.srcNode
                self.wireOrgDstNode = _hit_object.dstNode
                if _hit_object.currentSelectedCtrlPtIdx != -1:
                    self.useMouseRewire = True
                    if _hit_object.currentSelectedCtrlPtIdx == 0 or _hit_object.currentSelectedCtrlPtIdx == _len - 1:
                        _hit_object.save_hit()
                        _hit_object.unbind_all()
                    self.orgPos = _world_pos
                    self.curPos = _world_pos
            elif isinstance(_hit_object, StateChartNode):
                self.orgPos = _world_pos
                self.curPos = _world_pos
        else:
            self.rbStartPos = _pos
            self.rbDrawRect = True
            self.blockGraphEvent = True
            self._reset_selected_items_style()
            self.selectedItems.clear()
        super(GUIModeMouse, self).on_left_down(event)

    def on_left_up(self, event):
        _hit_object = self.canvas.objectUnderMouse
        _canvas_parent = self.canvas.GetParent()
        _ctrl_key_state = wx.GetKeyState(wx.WXK_CONTROL)
        if _ctrl_key_state:
            pass
        else:
            if self.selectedItems:
                for item in self.selectedItems:
                    if isinstance(item, TransitionWireShape):
                        self.useMouseRewire = False
                        if item.srcNode is None or item.dstNode is None:
                            if _canvas_parent:
                                _canvas_parent.remove_connection_pair(item, self.wireOrgSrcNode, self.wireOrgDstNode)
                        else:
                            if _canvas_parent:
                                _canvas_parent.update_connection_pair(item, self.wireOrgSrcNode, self.wireOrgDstNode)
                            item.restore_hit()
                            item.currentSelectedCtrlPtIdx = -1
                if _hit_object is None:
                    self.selectedItems.clear()
            self.curPos = None
            self.orgPos = None
            self.wireOrgSrcNode = None
            self.wireOrgDstNode = None
        if self.rbDrawRect:
            self.rbDrawRect = False
            self.blockGraphEvent = False
            self.rbRect = None
            if self.rbRect:
                _world_rect = (self.canvas.pixel_to_world(self.rbRect[0]),
                               self.canvas.scale_pixel_to_world(self.rbRect[1]))
                # wx.CallAfter(self.CallBack, _world_rect)
                print('rb_band is already', _world_rect)
        self.canvas.draw(True)
        super(GUIModeMouse, self).on_left_up(event)

    def on_middle_down(self, event):
        self.canvas.SetCursor(self.panGrabCursor)
        self.panStartMove = N.array(event.GetPosition())
        self.panMidMove = self.panStartMove
        self.panPrevMoveXY = (0, 0)
        super(GUIModeMouse, self).on_middle_down(event)

    def on_middle_up(self, event):
        self.canvas.SetCursor(self.cursor)
        if self.panStartMove is not None:
            self.panEndMove = N.array(event.GetPosition())
            _diff_move = self.panMidMove - self.panEndMove
            self.canvas.move_image(_diff_move, 'Pixel', redraw=True)
        super(GUIModeMouse, self).on_middle_up(event)

    def on_motion(self, event: wx.MouseEvent):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        _hit_object = self.canvas.objectUnderMouse
        if event.Dragging():
            if event.LeftIsDown():
                if self.selectedItems:
                    for item in self.selectedItems:
                        self._update_position(_world_pos)
                        _pos_diff = self._get_position_diff()
                        if isinstance(item, StateChartNode):
                            item.move(_pos_diff)
                            for in_wire in item.inWires:
                                in_wire.set_dst_point(in_wire.dstPt + _pos_diff)
                            for out_wire in item.outWires:
                                out_wire.set_src_point(out_wire.srcPt + _pos_diff)
                        elif isinstance(item, TransitionWireShape):
                            _object_at = self.canvas.object_at(_world_pos)
                            self._on_rewire(item, _pos_diff, _object_at, _world_pos)
                    self.canvas.draw(True)
                else:
                    if self.rbDrawRect:
                        self._on_draw_rubber_band(event)
            elif event.MiddleIsDown() and self.panStartMove is not None:
                self.panEndMove = N.array(_pos)
                _diff_move = self.panMidMove - self.panEndMove
                # reset the canvas without re-drawing
                self.canvas.move_image(_diff_move, 'Pixel', redraw=False)
                self.panMidMove = self.panEndMove
                self.panMoveTimer.Start(self.panRedrawDelayMs, oneShot=True)
        super(GUIModeMouse, self).on_motion(event)

    def on_key_down(self, event: wx.KeyEvent):
        _k_code = event.GetKeyCode()
        if _k_code == wx.WXK_DELETE or _k_code == wx.WXK_NUMPAD_DELETE:
            if self.selectedItems:
                _lst = [x for x in self.selectedItems]
                pub.sendMessage(EnumAppSignals.sigV2VGuiModeDelItemRequested, items=_lst)

    def update_screen(self):
        # The screen has been re-drawn, so StartMove needs to be reset.
        self.panStartMove = self.panMidMove
