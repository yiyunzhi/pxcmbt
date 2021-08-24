import wx
from .panel_header import HeaderPanel
from .panel_canvas_dot_graph import CompoundCanvasDotGraphViewPanel


class CanvasDotGraphViewerDialog(wx.Dialog):
    def __init__(self, img_name, parent, wx_id=wx.ID_ANY, title='CanvasDotGraphViewer', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='CanvasDotGraphViewerDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.headerPanel=HeaderPanel('', '', parent=self)
        self.viewerPanel = CompoundCanvasDotGraphViewPanel(self, img_name)
        # bind event

        # layout
        self.mainSizer.Add(self.headerPanel, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.viewerPanel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)
