import math
import wx
from application.define import *
#from .shape_wire import WireNodeShape


class PortShape( object ):

    def __init__( self, text, pos, radius, type_, node ):
        self._text = text
        self._node = node
        self._pos = wx.Point( pos[0], pos[1] )  # In node space
        self.radius = radius
        self._type = type_

        self._wires = []

    def GetText( self ):
        return self._text

    def SetText( self, text ):
        self._text = text

    def GetType( self ):
        return self._type

    def SetType( self, type_ ):
        self._type = type_

    def GetNode( self ):
        return self._node

    def SetNode( self, node ):
        self._node = node

    def GetPosition( self ):
        return self._pos

    def SetPosition( self, pos ):
        self._pos = pos

    def GetWires( self ):
        return self._wires

    def Draw( self, dc ):
        final = self._pos + self._node.GetRect().GetPosition()
        dc.SetPen( wx.Pen( 'grey',style=wx.TRANSPARENT ) )
        dc.SetBrush( wx.Brush( 'black', wx.SOLID ) )
        dc.DrawCircle( final.x, final.y, self.radius )

        # HAXXOR
        newFont = wx.SystemSettings.GetFont( wx.SYS_DEFAULT_GUI_FONT )
        tdc = wx.WindowDC( wx.GetApp().GetTopWindow() )
        tdc.SetFont( newFont )
        w, h = tdc.GetTextExtent( self._text )

        dc.SetFont( newFont )
        if self._type == PORT_TYPE_IN:
            x = final.x + PORT_TITLE_MARGIN
        else:
            x = final.x - w - PORT_TITLE_MARGIN

        dc.DrawText( self._text, x, final.y - h / 2 )

    def HitTest( self, pos ):
        pnt = pos - self._pos
        dist = math.sqrt( math.pow( pnt.x, 2 ) + math.pow( pnt.y, 2 ) )
        if math.fabs( dist ) < PORT_HIT_RADIUS:
            return True

    def CanConnect( self ):
        pass

    def Connect( self, dstPort ):
        print('Connecting:', self, '->', dstPort)
        pt1 = self.GetNode().GetRect().GetPosition() + self.GetPosition()
        pt2 = dstPort.GetNode().GetRect().GetPosition() + dstPort.GetPosition()
        wire = Wire( pt1, pt2, self.GetType() )
        wire.srcNode = self.GetNode()
        wire.dstNode = dstPort.GetNode()
        wire.srcPort = self
        wire.dstPort = dstPort
        self._wires.append( wire )
        dstPort.GetWires().append( wire )

        dc = self.GetNode().GetParent().pdc
        wire.Draw( dc )
        self.GetNode().GetParent().RefreshRect( wire.GetRect(), False )

    def Disconnect( self ):
        '''
        # HAXXOR
        for wire in self._wires:
            print 'del:', wire
            del wire.srcNode# = self.GetNode()
            del wire.dstNode# = dstPlug.GetNode()
            del wire.srcPlug# = self
            del wire.dstPlug# = dstPlug
            self.GetNode().GetParent().RefreshRect( wire.GetRect(), False )
        self._wires = []
            #print 'disconnect:', wire
        '''