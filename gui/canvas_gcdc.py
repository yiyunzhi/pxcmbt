import wx
from wx.lib.floatcanvas import FloatCanvas
from wx.lib.floatcanvas.FCObjects import DrawObject
import numpy as N
import time


class GCDCCanvas(FloatCanvas.FloatCanvas):
    def __init__(self, parent, wx_id=-1,
                 size=wx.DefaultSize,
                 projection_fun=None,
                 background_color="WHITE",
                 debug=False,
                 **kwargs):
        FloatCanvas.FloatCanvas.__init__(self, parent, id=wx_id,
                                         size=size,
                                         ProjectionFun=projection_fun,
                                         BackgroundColor=background_color,
                                         Debug=debug,
                                         **kwargs)

    def OnPaint(self, event):
        """On paint handler."""
        pdc = wx.PaintDC(self)
        pdc.Clear()
        dc = wx.GCDC(pdc)
        if self._ForegroundBuffer:
            dc.DrawBitmap(self._ForegroundBuffer, 0, 0)
        else:
            dc.DrawBitmap(self._Buffer, 0, 0)
        ## this was so that rubber band boxes and the like could get drawn here
        ##  but it looks like a wx.ClientDC is a better bet still.
        # try:
        #    self.GUIMode.DrawOnTop(dc)
        # except AttributeError:
        #    pass

    def Draw(self, force=False):
        if N.sometrue(self.PanelSize <= 2):
            # it's possible for this to get called before being properly initialized.
            return
        if self.Debug: start = time.time()
        _screen_dc = wx.ClientDC(self)
        _viewport_world = N.array((self.PixelToWorld((0, 0)), self.PixelToWorld(self.PanelSize)))
        self.ViewPortBB = N.array((N.minimum.reduce(_viewport_world), N.maximum.reduce(_viewport_world)))

        _mdc = wx.MemoryDC()
        _mdc.SelectObject(self._Buffer)
        _dc = wx.GCDC(_mdc)
        if self._BackgroundDirty or force:
            _dc.SetBackground(self.BackgroundBrush)
            _dc.Clear()
            if self._HTBitmap is not None:
                _ht_mdc = wx.MemoryDC()
                _ht_mdc.SelectObject(self._HTBitmap)
                _ht_dc = wx.GCDC(_ht_mdc)
                _ht_dc.Clear()
            else:
                _ht_dc = None
            if self.GridUnder is not None:
                self.GridUnder._Draw(_dc, self)
            self._DrawObjects(_dc, self._DrawList, _screen_dc, self.ViewPortBB, _ht_dc)
            self._BackgroundDirty = False
            del _ht_dc

        if self._ForeDrawList:
            # If an object was just added to the Foreground, there might not yet be a buffer
            if self._ForegroundBuffer is None:
                self._ForegroundBuffer = wx.Bitmap(self.PanelSize[0], self.PanelSize[1])
            _mdc = wx.MemoryDC()  # I got some strange errors (linewidths wrong) if I didn't make a new DC here
            _mdc.SelectObject(self._ForegroundBuffer)
            _dc.DrawBitmap(self._Buffer, 0, 0)
            if self._ForegroundHTBitmap is not None:
                _foreground_ht_mdc = wx.MemoryDC()
                _foreground_ht_mdc.SelectObject(self._ForegroundHTBitmap)
                _foreground_ht_dc = wx.GCDC(_foreground_ht_mdc)
                _foreground_ht_dc.Clear()
                if self._HTBitmap is not None:
                    # Draw the background HT buffer to the foreground HT buffer
                    _foreground_ht_dc.DrawBitmap(self._HTBitmap, 0, 0)
            else:
                _foreground_ht_dc = None
            self._DrawObjects(_dc,
                              self._ForeDrawList,
                              _screen_dc,
                              self.ViewPortBB,
                              _foreground_ht_dc)
        if self.GridOver is not None:
            self.GridOver._Draw(_dc, self)
        _screen_dc.Blit(0, 0, self.PanelSize[0], self.PanelSize[1], _mdc, 0, 0)
        # If the canvas is in the middle of a zoom or move,
        # the Rubber Band box needs to be re-drawn
        ##fixme: maybe GUIModes should never be None, and rather have a Do-nothing GUI-Mode.
        if self.GUIMode is not None:
            self.GUIMode.UpdateScreen()

        if self.Debug:
            print("Drawing took %f seconds of CPU time" % (time.time() - start))
            if self._HTBitmap is not None:
                self._HTBitmap.SaveFile('junk.png', wx.BITMAP_TYPE_PNG)

        # Clear the font cache. If you don't do this, the X font server
        # starts to take up Massive amounts of memory This is mostly a
        # problem with very large fonts, that you get with scaled text
        # when zoomed in.
        DrawObject.FontList = {}
