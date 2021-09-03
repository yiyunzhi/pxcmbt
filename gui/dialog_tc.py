import wx
from pubsub import pub
from application.class_test_server import MBTOnlineTestServer
from application.define import EnumAppSignals
from .panel_header import HeaderPanel
from .panel_tc_viewer import TCViewerPanel
from .panel_tc_controller import TCControllerPanel
from .panel_tc_log import TCConsolePanel


class TCDialog(wx.Dialog):
    def __init__(self, tcs_runner, parent, wx_id=wx.ID_ANY, title='TC', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='TCDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.testRunner = tcs_runner
        self.tccPanel = TCControllerPanel(self)
        self.tcvPanel = TCViewerPanel(self, tcs_runner)
        self.tclPanel = TCConsolePanel(parent=self)
        self.testServer = MBTOnlineTestServer(self.testRunner)
        self.SetMinSize((360, 480))
        # layout

        # bind event
        self.Bind(wx.EVT_CLOSE, self.on_close)
        pub.subscribe(self.on_ext_sig_ctrl_state_changed, EnumAppSignals.sigV2VTCCtrlStateChanged.value)
        # layout
        self.mainSizer.Add(HeaderPanel('TestCaseManager', 'TestCaseManager', parent=self), 0,
                           wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tccPanel, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tclPanel, 1, wx.EXPAND | wx.ALL, 10)
        self.mainSizer.Add(self.tcvPanel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_close(self, evt):
        self.testServer.stop()
        self.testRunner.reset()
        evt.Skip()

    def on_ext_sig_ctrl_state_changed(self, state):
        if state:
            self.testServer.start()
        else:
            self.testServer.stop()
