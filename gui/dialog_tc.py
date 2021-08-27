import wx
from .panel_header import HeaderPanel
from .panel_tc_viewer import TCViewerPanel
from .panel_tc_controller import TCControllerPanel
from .panel_tc_log import TCConsolePanel


class TCDialog(wx.Dialog):
    def __init__(self, tcs, parent, wx_id=wx.ID_ANY, title='TC', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='TCDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.tccPanel = TCControllerPanel(self)
        self.tcvPanel = TCViewerPanel(self, tcs)
        self.tclPanel = TCConsolePanel(parent=self)
        self.SetMinSize((360, 480))
        # layout

        # bind event

        # layout
        self.mainSizer.Add(HeaderPanel('TestCaseManager', 'TestCaseManager', parent=self), 0,
                           wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tccPanel, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tclPanel, 1, wx.EXPAND | wx.ALL, 10)
        self.mainSizer.Add(self.tcvPanel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()
