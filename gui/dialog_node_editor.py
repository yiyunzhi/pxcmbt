import wx
from application.class_mbt_event import MBTEventManager
from .panel_event_selector import EventSelectorPanel


class GuiNodeEditorPanel(wx.Panel):
    def __init__(self, evt_mgr, item, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.evtMgr = evt_mgr
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.item = item
        self._init_ui()
        self.Layout()
        self.Fit()

    def _init_ui(self):
        self._generalBagSizer = wx.GridBagSizer(5, 5)
        self._generalBoxSizer = wx.StaticBoxSizer(
            wx.StaticBox(self, -1, 'General'),
            wx.VERTICAL)
        self._enterEvtBoxSizer = wx.StaticBoxSizer(
            wx.StaticBox(self, -1, 'Emitted Events by Enter'),
            wx.VERTICAL)
        self._exitEvtBoxSizer = wx.StaticBoxSizer(
            wx.StaticBox(self, -1, 'Emitted Events by Exit'),
            wx.VERTICAL)
        self.ctrlNameLabel = wx.StaticText(self, wx.ID_ANY, 'Name:')
        self.ctrlNameEdit = wx.TextCtrl(self, wx.ID_ANY, self.item.nameText)
        self.ctrlEventsEnterEdit = EventSelectorPanel(self.evtMgr, self)
        self.ctrlEventsExitEdit = EventSelectorPanel(self.evtMgr, self)
        _enter_event_model = self.item.enterEventModel
        _exit_event_model = self.item.exitEventModel
        self.ctrlEventsEnterEdit.set_selected_events(_enter_event_model.events)
        self.ctrlEventsExitEdit.set_selected_events(_exit_event_model.events)
        self._generalBagSizer.Add(self.ctrlNameLabel, (0, 0), flag=wx.TOP, border=4)
        self._generalBagSizer.Add(self.ctrlNameEdit, (0, 1), span=(1, 10), flag=wx.EXPAND)

        self._generalBoxSizer.Add(self._generalBagSizer, 1, wx.EXPAND)
        self._enterEvtBoxSizer.Add(self.ctrlEventsEnterEdit, 1, wx.EXPAND)
        self._exitEvtBoxSizer.Add(self.ctrlEventsExitEdit, 1, wx.EXPAND)
        self.mainSizer.Add(self._generalBoxSizer, 0, wx.EXPAND)
        self.mainSizer.Add(self._enterEvtBoxSizer, 1, wx.EXPAND)
        self.mainSizer.Add(self._exitEvtBoxSizer, 1, wx.EXPAND)


class NodeEditorDialog(wx.Dialog):
    def __init__(self, evt_data, item, parent, wx_id=wx.ID_ANY, title='NodeEditor', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='NodeEditorDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.evtMgr = MBTEventManager()
        self.evtMgr.deserialize(evt_data)
        self._editorPanel = GuiNodeEditorPanel(self.evtMgr, item, self)
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
        self.Bind(wx.EVT_BUTTON, self.on_ok_clicked, _btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_clicked, _btn_cancel)
        self.Layout()
        self.Fit()

    def on_ok_clicked(self, evt):
        _item = self._editorPanel.item
        _name_text = self._editorPanel.ctrlNameEdit.GetValue()
        _enter_events = self._editorPanel.ctrlEventsEnterEdit.get_selected_events()
        _exit_events = self._editorPanel.ctrlEventsExitEdit.get_selected_events()
        _item.enterEventModel.clear()
        _item.exitEventModel.clear()
        for a, b in _enter_events:
            _item.enterEventModel.update(a, b)
        for a, b in _exit_events:
            _item.exitEventModel.update(a, b)
        _item.set_name(_name_text)
        _item.update_event_desc_text()
        evt.Skip()

    def on_cancel_clicked(self, evt):
        evt.Skip()

    def get_node_name(self):
        return self._editorPanel.ctrlNameEdit.GetValue()

    def set_enter_events(self, list_evts):
        self._editorPanel.ctrlEventsEnterEdit.set_selected_events(list_evts)

    def set_exit_events(self, list_evts):
        self._editorPanel.ctrlEventsExitEdit.set_selected_events(list_evts)


class NodeNoteEditorDialog(wx.Dialog):
    def __init__(self, item, parent, wx_id=wx.ID_ANY, title='NodeNoteEditor', size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='NodeNoteEditorDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.item = item
        self.noteTextEdit = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE)
        self.noteTextEdit.SetValue(self.item.text)
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
        self.mainSizer.Add(self.noteTextEdit, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.on_ok_clicked, _btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_clicked, _btn_cancel)
        self.Layout()
        self.Fit()

    def on_ok_clicked(self, evt):
        self.item.set_text(self.noteTextEdit.GetValue())
        evt.Skip()

    def on_cancel_clicked(self, evt):
        evt.Skip()
