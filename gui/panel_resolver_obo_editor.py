import wx
from .panel_obo_selector import OBOSelectorPanel
from application.class_observable import MBTOBOManager


class ResolverOBOEditPanel(wx.Panel):
    def __init__(self, obo_mgr, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboEditorSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.processedOboMgr = None
        self.oboSelectorPanel = OBOSelectorPanel(obo_mgr, self)
        # bind events
        # layouts
        self.oboEditorSizer.Add(self.oboSelectorPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.oboEditorSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def clear(self):
        self.processedOboMgr = None
        self.oboSelectorPanel.oboList.DeleteAllItems()

    def set_data(self, obo_mgr: MBTOBOManager):
        self.processedOboMgr = obo_mgr
        _obos = list()
        for k, v in obo_mgr.get_all_obos().items():
            _obos.append((v.name, v.get_data_in_string(), v.uuid))
        self.oboSelectorPanel.set_selected_obos(_obos)

