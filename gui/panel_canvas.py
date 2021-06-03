import wx
import wx.adv
import json
from gui.define_gui import *
from application.define import EnumPanelRole
from application.wire import Wire
from application.node import Node


# todo: canvas scale, selection, selected
# todo: scroll, middlekey move
class CanvasPanel2(wx.Panel):
    def __init__(self, parent, wx_id, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, wx_id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.uuid = None
        self.role = EnumPanelRole.STATE_CHART_CANVAS
        self.canvasToolbarMode = EnumCanvasToolbarMode.POINTER
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

    def get_canvas_toolbar_mode(self):
        return self.canvasToolbarMode

    def set_canvas_toolbar_mode(self, mode: EnumCanvasToolbarMode):
        self.canvasToolbarMode = mode

    def on_mouse_wheel(self, evt: wx.MouseEvent):
        _k_ctrl_pressed = wx.GetKeyState(wx.WXK_CONTROL)
        print('on_mouse_wheel')
        if _k_ctrl_pressed:
            self.SetScale(0.5, 0.5)
            _wheel_axis = evt.GetWheelAxis()
            _wheel_delta = evt.GetWheelDelta()
            _wheel_rt = evt.GetWheelRotation()
            print(_wheel_axis, _wheel_delta, _wheel_rt, evt.IsPageScroll(), evt.GetMagnification(),
                  evt.GetLinesPerAction())

        evt.Skip()


class CanvasPanel(wx.ScrolledWindow):
    def __init__(self, parent, wx_id, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, wx_id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.uuid = None
        self.role = EnumPanelRole.STATE_CHART_CANVAS
        self.nodes = {}
        self.srcNode = None
        self.srcPort = None
        self.tmpWire = None
        self.lastPnt = wx.Point(0, 0)
        # ui initial setting
        self.maxWidth = CANVAS_MAX_W
        self.maxHeight = CANVAS_MAX_H
        self.canvasToolbarMode = EnumCanvasToolbarMode.POINTER
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20, 20)

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

    def on_mouse_wheel(self, evt: wx.MouseEvent):
        _k_ctrl_pressed = wx.GetKeyState(wx.WXK_CONTROL)
        print('on_mouse_wheel')
        if _k_ctrl_pressed:
            self.SetScale(0.5, 0.5)
            _wheel_axis = evt.GetWheelAxis()
            _wheel_delta = evt.GetWheelDelta()
            _wheel_rt = evt.GetWheelRotation()
            print(_wheel_axis, _wheel_delta, _wheel_rt, evt.IsPageScroll(), evt.GetMagnification(),
                  evt.GetLinesPerAction())

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
