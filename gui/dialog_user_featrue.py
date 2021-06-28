import wx
from .panel_header import HeaderPanel


class PromptUserFeatureNameDialog(wx.Dialog):
    def __init__(self, ref_fun_name_checker, parent, wx_id=wx.ID_ANY, title='PromptUserFeatureName',
                 size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='PromptUserFeatureNameDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.refFuncNameChecker = ref_fun_name_checker
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._formSizer = wx.GridBagSizer(5, 5)
        self.ufNameLabel = wx.StaticText(self, wx.ID_ANY, 'UserFeatureName:')
        self.ufNameTextEdit = wx.TextCtrl(self, wx.ID_ANY)
        self.ufNameExistMsgLabel = wx.StaticText(self, wx.ID_ANY, '')
        self.ufNameExistMsgLabel.SetForegroundColour(wx.RED)
        # layout
        self._formSizer.Add(self.ufNameLabel, (0, 0))
        self._formSizer.Add(self.ufNameTextEdit, (0, 1))
        self._formSizer.Add(self.ufNameExistMsgLabel, (1, 0), span=(1, 10))
        self._btnSizer = wx.StdDialogButtonSizer()
        _btn_ok = wx.Button(self, wx.ID_OK)
        _btn_ok.SetHelpText("The OK button completes the dialog")
        _btn_ok.SetDefault()
        self._btnSizer.AddButton(_btn_ok)

        _btn_cancel = wx.Button(self, wx.ID_CANCEL)
        _btn_cancel.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        self._btnSizer.AddButton(_btn_cancel)
        self._btnSizer.Realize()
        # bind event
        _btn_ok.Bind(wx.EVT_BUTTON, self.on_ok_clicked)
        self.ufNameTextEdit.Bind(wx.EVT_CHAR, self.on_name_entered)
        # layout
        self.mainSizer.Add(HeaderPanel('Prompt UserFeature name', 'Prompt UserFeature name', parent=self), 1,
                           wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._formSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_name_entered(self, evt):
        self.ufNameExistMsgLabel.SetLabel('')
        evt.Skip()

    def on_ok_clicked(self, evt):
        _name = self.ufNameTextEdit.GetValue()
        if not _name or not _name.strip():
            self.ufNameExistMsgLabel.SetLabel('name can not empty')
            return
        if self.refFuncNameChecker(self.ufNameTextEdit.GetValue()):
            self.ufNameExistMsgLabel.SetLabel('name %s is already exist' % _name)
            return
        evt.Skip()
