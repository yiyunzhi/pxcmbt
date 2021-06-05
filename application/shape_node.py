import wx
from wx.adv import PseudoDC
from .shape_port import PortShape
from application.define import *
from gui.define_gui import EnumShapeConnectionStyle, EnumShapeStyle


# todo: BaseNodeShape should from Serializable inherited.

class BaseNodeShape:
    def __init__(self, parent, sh_id):
        self.parent = parent
        self.connectionStyle = EnumShapeConnectionStyle.ANYWHERE
        self.style = EnumShapeStyle.STYLE_DEFAULT
        self.position = wx.DefaultPosition
        self.relativePosition = wx.DefaultPosition
        self.userData = None
        self.borderPen = None
        self.fillBrush = None
        self.childShapes = dict()
        self.borderPen = wx.TRANSPARENT_PEN
        self.fillBrush = wx.TRANSPARENT_BRUSH
        self.hoverBorderPen = wx.TRANSPARENT_PEN
        self.hoverFillBrush = wx.TRANSPARENT_BRUSH
        self.isVisible = True
        self.isSelected = False
        self.isMouseOvered = False
        self.lstHandles = list()
        self.lstConnectionPts = list()
        if sh_id == wx.ID_ANY:
            self._id = wx.NewId()
        else:
            self._id = sh_id

    def has_style(self, style):
        return (self.style & style) != 0

    def add_style(self, style):
        self.style |= style

    def has_children(self):
        return len(self.childShapes) != 0

    def add_child(self, child):
        assert isinstance(child, BaseNodeShape)
        _id = child.get_id()
        if _id not in self.childShapes:
            child.set_position(self.position)
            self.childShapes.update({_id: child})

    def remove_child(self, child):
        if isinstance(child, BaseNodeShape):
            _id = child.get_id()
        elif isinstance(child, int):
            _id = child
        else:
            return
        if _id in self.childShapes:
            self.childShapes.pop(_id)

    def get_children_list(self):
        return list(self.childShapes.values())

    def get_child(self, child_id):
        return self.childShapes.get(child_id)

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        if self.has_style(EnumShapeStyle.REPARENT):
            self.parent.remove_child(self)
            self.parent = parent

    def get_id(self):
        return self._id

    def get_user_data(self):
        return self.userData

    def set_user_data(self, data):
        self.userData = data

    def get_connection_style(self):
        return self.connectionStyle

    def set_connection_style(self, style: EnumShapeConnectionStyle):
        self.connectionStyle = style

    def get_border_pen(self):
        return self.borderPen

    def set_border_pen(self, pen: wx.Pen):
        self.borderPen = pen

    def get_fill_brush(self):
        return self.borderPen

    def set_fill_brush(self, brush: wx.Brush):
        self.fillBrush = brush

    def set_position(self, pos):
        self.position = pos

    def get_position(self):
        return self.position

    def set_relative_position(self, pos):
        self.relativePosition = pos

    def get_relative_position(self):
        return self.relativePosition

    def contains(self, pt):
        raise NotImplemented()

    def get_bounding_box(self):
        raise NotImplemented()

    def draw(self, pdc):
        raise NotImplemented()


class NodeShape(object):
    def __init__(self, parent, text='', colour='white', data=None, rect=wx.ID_ANY, id=wx.ID_ANY, ins=None, outs=None):
        self.connectionStyle = EnumShapeConnectionStyle.ANYWHERE
        self.style = EnumShapeStyle.STYLE_DEFAULT
        self._parent = parent

        self._text = text
        self._colour = colour
        self._data = data
        self._rect = rect  # wx.Rect()
        self._ports = []

        if id == wx.ID_ANY:
            self._id = wx.NewId()
        else:
            self._id = id

        # HAXXOR
        x, y, w, h = self._rect.Get()
        for i, portName in enumerate(list(ins) + list(outs)):
            portType = PORT_TYPE_IN
            x = PORT_MARGIN
            if portName in outs:
                x = w - x
                portType = PORT_TYPE_OUT
            port = Port(portName, (x, 40 + PORT_SPACING * i), PORT_RADIUS, portType, self)
            self._ports.append(port)

    def GetId(self):
        return self._id

    def SetId(self, id_):
        self._id = id_

    def GetType(self):
        return self._type

    def SetType(self, type_):
        self._type = type_

    def GetText(self):
        return self._text

    def SetText(self, text):
        self._text = text

    def GetData(self):
        return self._data

    def SetData(self, data):
        self._data = data

    def GetRect(self):
        return self._rect

    def SetRect(self, rect):
        self._rect = rect

    def GetColour(self):
        return self._colour

    def SetColour(self, colour):
        self._colour = colour

    def IsSelected(self):
        pass

    def Enable(self, enable=True):
        self._enabled = enable

    def IsEnabled(self):
        return self._enabled

    def GetPorts(self):
        return self._ports

    def FindPort(self, portName):
        for port in self._ports:
            if port.GetText() == portName:
                return port

    def GetParent(self):
        return self._parent

    def HitTest(self, x, y):
        for port in self._ports:
            if port.HitTest(wx.Point(x, y) - self._rect.GetPosition()):
                return port

    def Draw(self, dc):
        x, y, w, h = self._rect.Get()

        dc.SetId(self._id)

        dc.SetPen(wx.Pen('black', 1))
        dc.SetBrush(wx.Brush(self._colour, wx.SOLID))
        dc.DrawRoundedRectangle(x, y, w, h, ROUND_CORNER_RADIUS)

        newFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        newFont.SetWeight(wx.BOLD)
        dc.SetFont(newFont)

        dc.DrawText(self._text, x + TITLE_INSET_X, y + TITLE_INSET_Y)

        # Draw ins / outs.
        for port in self._ports:
            port.Draw(dc)

        dc.SetIdBounds(self._id, self._rect)
