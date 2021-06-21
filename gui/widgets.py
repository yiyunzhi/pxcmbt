import wx


class AutocompleteComboBox(wx.ComboBox):
    def __init__(self, parent, choices=[], style=0, **kwargs):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, style=style | wx.CB_DROPDOWN, choices=choices, **kwargs)
        self.choices = choices
        self.Bind(wx.EVT_TEXT, self.on_text)
        self.Bind(wx.EVT_KEY_DOWN, self.on_press)
        self.ignoreEvtText = False
        self.deleteKey = False

    def on_press(self, event):
        if event.GetKeyCode() == 8:
            self.deleteKey = True
        event.Skip()

    def on_text(self, event):
        _current_text = event.GetString()
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        if self.deleteKey:
            self.deleteKey = False
            if self.preFound:
                _current_text = _current_text[:-1]

        self.preFound = False
        for choice in self.choices:
            if choice.startswith(_current_text):
                self.ignoreEvtText = True
                self.SetValue(choice)
                self.SetInsertionPoint(len(_current_text))
                self.SetTextSelection(len(_current_text), len(choice))
                self.preFound = True
                break
