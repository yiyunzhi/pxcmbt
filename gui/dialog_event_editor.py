import wx
from .panel_event_detail import EventDetailPanel


class EventDetailEditorDialog(wx.Dialog):
    def __init__(self, parent, wx_id=wx.ID_ANY, title='EventDetailEditor', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='EventDetailEditorDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.detailPanel = EventDetailPanel(self)
        # layout
        self._btnSizer = wx.StdDialogButtonSizer()
        _btn_ok = wx.Button(self, wx.ID_OK)
        _btn_ok.SetHelpText("The OK button completes the dialog")
        _btn_ok.SetDefault()
        self._btnSizer.AddButton(_btn_ok)

        _btn_cancel = wx.Button(self, wx.ID_CANCEL)
        _btn_cancel.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        self._btnSizer.AddButton(_btn_cancel)
        self._btnSizer.Realize()
        self.mainSizer.Add(self.detailPanel, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        # self.Bind(wx.EVT_BUTTON, self.on_ok_clicked, _btn_ok)
        # self.Bind(wx.EVT_BUTTON, self.on_cancel_clicked, _btn_cancel)
        self.Layout()
        self.Fit()

    def get_event(self):
        return self.detailPanel.get_data()
