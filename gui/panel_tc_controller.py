import wx
import wx.dataview as dv
from pubsub import pub
from application.define import EnumAppSignals, EnumTCStatus
from .panel_header import HeaderPanel
from .util_icon_repo import UtilIconRepo


class TCDetailTooltipFormatter:
    def __init__(self):
        pass


class TCControllerPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_TCC'
        self._iconRepo = UtilIconRepo()
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.tlSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.runStopBtn = wx.ToggleButton(self, wx.ID_ANY, 'RUN')
        # bind event
        self.runStopBtn.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn_toggled)
        # pub.subscribe(self.on_ext_sig_current_tc_changed, EnumAppSignals.sigV2VCurrentTCChanged.value)
        # pub.subscribe(self.on_ext_sig_current_tc_status_changed, EnumAppSignals.sigV2VCurrentTCStatusChanged.value)
        self.tlSizer.Add(self.runStopBtn, 0)
        # self.mainSizer.Add(HeaderPanel('Control of Testcases', 'Control of Testcases', parent=self), 0,
        #                    wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tlSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_btn_toggled(self, evt):
        _state = evt.GetEventObject().GetValue()
        if _state:
            self.runStopBtn.SetLabelText('STOP')
        else:
            self.runStopBtn.SetLabelText('RUN')
        pub.sendMessage(EnumAppSignals.sigV2VTCCtrlStateChanged.value, state=_state)
