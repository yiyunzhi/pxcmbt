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


class FeaturePropsContentPanel(PropsContentPanel):
    # todo: in next version
    def __init__(self, feature_data_item, project, **kwargs):
        PropsContentPanel.__init__(self, feature_data_item.uuid, feature_data_item.role, **kwargs)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.project = project
        self.SetSizer(self.mainSizer)
        self.propMgr = project.get_feature_properties(self, feature_data_item)
        self.mainSizer.Add(self.propMgr, 1, wx.EXPAND)
        self.Layout()
        self.Fit()

    def get_props(self, *args):
        pass

    def set_props(self, *args):
        pass


class OBOPropsContentPanel(PropsContentPanel):
    def __init__(self, obo=None, **kwargs):
        PropsContentPanel.__init__(self, None, None, **kwargs)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.obo = obo
        self._pg = self._get_prop_control()
        self.mainSizer.Add(self._pg, 1, wx.EXPAND)
        self.Layout()
        self.Fit()

    def set_obo(self, obo):
        self.obo = obo

    def _get_prop_control(self):
        _pg_main = wxpg.PropertyGridManager(self, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED|wxpg.PG_TOOLBAR)
        _pg1 = _pg_main.AddPage('OBO')
        if self.obo is not None:
            _pg_uuid = wxpg.StringProperty("uuid", 'uuid', value=self.obo.uuid)
            _pg1.SetPropertyReadOnly(_pg_uuid)
            _pg1.Append(_pg_uuid)

            _pg_type = wxpg.StringProperty("type", 'obotype', value=self.obo.type)
            _pg1.SetPropertyReadOnly(_pg_type)
            _pg1.Append(_pg_type)

            _pg_name = wxpg.StringProperty("name ", 'oboname', value=self.obo.name)
            _pg1.SetPropertyReadOnly(_pg_name)
            _pg1.Append(_pg_name)

            _pg_desc = wxpg.LongStringProperty("description ", 'description', value=self.obo.description)
            _pg1.SetPropertyReadOnly(_pg_desc)
            _pg1.Append(_pg_desc)

            _pg2 = _pg_main.AddPage('OBOData')
            for k, v in self.obo.data.items():
                _pg2.Append(wxpg.PropertyCategory("%s" % v.name))
                _pg_name = wxpg.StringProperty("name ", 'obodataname_%s'%k, value=v.name)
                _pg2.SetPropertyReadOnly(_pg_name)
                _pg2.Append(_pg_name)

                _pg_type = wxpg.StringProperty("type ", 'obodatatype_%s'%k, value=v.dataType)
                _pg2.SetPropertyReadOnly(_pg_type)
                _pg2.Append(_pg_type)

                _pg_type = wxpg.StringProperty("value ", 'obodatavalue_%s'%k, value=v.to_string())
                _pg2.SetPropertyReadOnly(_pg_type)
                _pg2.Append(_pg_type)

        return _pg_main

    def get_props(self, *args):
        pass

    def set_props(self, *args):
        pass
