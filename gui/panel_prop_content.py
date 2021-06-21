import wx
import wx.propgrid as wxpg


class PropsContentPanel(wx.Panel):
    def __init__(self, uuid, role, **kwargs):
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


class CanvasNodePropContentPanel(PropsContentPanel):
    def __init__(self, node_item, **kwargs):
        PropsContentPanel.__init__(self, node_item.uuid, node_item.role, **kwargs)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.propMgr = node_item.get_properties(self)
        self.mainSizer.Add(self.propMgr, 1, wx.EXPAND)
        self.Layout()
        self.Fit()

    def get_props(self, *args):
        pass

    def set_props(self, *args):
        pass
