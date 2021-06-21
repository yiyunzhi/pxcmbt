import wx
import wx.lib.filebrowsebutton as filebrowser
from .panel_header import HeaderPanel


class NewProjectDialog(wx.Dialog):
    def __init__(self, default_path, parent, wx_id=wx.ID_ANY, title='NewProject', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='NewProjectDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._formSizer = wx.GridBagSizer(5, 5)
        self.projectPath = default_path
        self.projNameLabel = wx.StaticText(self, wx.ID_ANY, 'ProjectName:')
        self.projNameTextEdit = wx.TextCtrl(self, wx.ID_ANY)
        self.projPathEdit = filebrowser.FileBrowseButton(self, wx.ID_ANY, changeCallback=self.fbb_callback)
        self.projPathEdit.SetValue(default_path)
        self.projPathEdit.SetLabel('ProjectPath:  ')
        # layout
        self._formSizer.Add(self.projNameLabel, (0, 0))
        self._formSizer.Add(self.projNameTextEdit, (0, 1))
        self._formSizer.Add(self.projPathEdit, (1, 0), span=(1, 25), flag=wx.EXPAND)
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

        # layout
        self.mainSizer.Add(HeaderPanel('New Project', 'create a project', parent=self), 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._formSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def fbb_callback(self, evt):
        self.projectPath = evt.GetString()
