import wx


class GuiNodeEditorPanel(wx.Panel):
    def __init__(self, item, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.item = item
        self._init_ui()
        self.SetAutoLayout(True)

    def _init_ui(self):
        self._inSizer = wx.GridBagSizer(5, 5)
        self._inBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'General todo: sortable, checkable event list'), wx.VERTICAL)
        self._inBoxSizer.Add(self._inSizer)
        self.ctrlNameLabel = wx.StaticText(self, wx.ID_ANY, 'Name:')
        self.ctrlNameEdit = wx.TextCtrl(self, wx.ID_ANY, self.item.nameText)
        self.ctrlEventsEnterLabel = wx.StaticText(self, wx.ID_ANY, 'Events Enter:')
        self.ctrlEventsEnterEdit = wx.TextCtrl(self, wx.ID_ANY, self.item.evtDescText, style=wx.TE_MULTILINE)
        self.ctrlEventsExitLabel = wx.StaticText(self, wx.ID_ANY, 'Events Exit:')
        self.ctrlEventsExitEdit = wx.TextCtrl(self, wx.ID_ANY, self.item.evtDescText, style=wx.TE_MULTILINE)
        self._inSizer.Add(self.ctrlNameLabel, pos=(0, 0), flag=wx.TOP, border=4)
        self._inSizer.Add(self.ctrlNameEdit, pos=(0, 1))
        self._inSizer.Add(self.ctrlEventsEnterLabel, pos=(1, 0), flag=wx.TOP, border=4)
        self._inSizer.Add(self.ctrlEventsEnterEdit, pos=(1, 1), span=(1, 5), flag=wx.EXPAND)
        self._inSizer.Add(self.ctrlEventsExitLabel, pos=(2, 0), flag=wx.TOP, border=4)
        self._inSizer.Add(self.ctrlEventsExitEdit, pos=(2, 1), span=(1, 5), flag=wx.EXPAND)
        self.mainSizer.Add(self._inBoxSizer, 1, wx.EXPAND)


class NodeEditorDialog(wx.Dialog):
    def __init__(self, item, parent, id=wx.ID_ANY, title='NodeEditor', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='NodeEditorDialog'):
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self._editorPanel = GuiNodeEditorPanel(item, self)
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

        self.mainSizer.Add(self._editorPanel, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        self.SetAutoLayout(True)
        self.Fit()
