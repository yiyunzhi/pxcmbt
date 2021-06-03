import wx

class PropContainerPanel(wx.Panel):

    def __init__(self, **kwargs):
        wx.Panel.__init__(self, **kwargs)
        self._vSizer = wx.BoxSizer(wx.VERTICAL)
        self._propsContentPanels = list()
        #EnumRackPanelSignals.sigV2MSessionNameChanged.connect(self.on_session_name_changed)
        self.SetSizer(self._vSizer)
        self.Layout()
        self.Fit()

    def get_panel_by_uuid(self, uuid):
        _res = None
        for x in self._propsContentPanels:
            if x.uuid == uuid:
                _res = x
                break
        return _res

    def on_session_name_changed(self, sender, uuid, new_name):
        _panel = self.get_panel_by_uuid(uuid)
        if _panel:
            _panel.p_name = new_name

    def hide_panels(self, exclusive=[]):
        [x.Hide() for x in self._propsContentPanels if x not in exclusive]

    def toggle_panel_by_uuid(self, uuid):
        for x in self._propsContentPanels:
            if x.uuid != uuid:
                x.Hide()
            else:
                x.Show(True)

    def set_content(self, prop_content_inst):
        if prop_content_inst in self._propsContentPanels:
            self.hide_panels([prop_content_inst])
        else:
            self.Freeze()
            self.hide_panels()
            prop_content_inst.Reparent(self)
            self._vSizer.Add(prop_content_inst, 1, wx.EXPAND)
            self._propsContentPanels.append(prop_content_inst)
            self._vSizer.Layout()
            self.Refresh()
            self.Update()
            self.Thaw()


class PropsContentPanel(wx.Panel):
    def __init__(self, role, uuid, **kwargs):
        wx.Panel.__init__(self, **kwargs)
        self.role = role
        self.uuid = uuid
        self.name = ''

    @property
    def p_name(self):
        return self.name

    @p_name.setter
    def p_name(self, name):
        self.name = name

    def get_props(self, *args):
        raise NotImplementedError()

    def set_props(self, *args):
        raise NotImplementedError()