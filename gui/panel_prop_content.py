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
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED | wxpg.PG_TOOLBAR)
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
                _pg_name = wxpg.StringProperty("name ", 'obodataname_%s' % k, value=v.name)
                _pg2.SetPropertyReadOnly(_pg_name)
                _pg2.Append(_pg_name)

                _pg_type = wxpg.StringProperty("type ", 'obodatatype_%s' % k, value=v.dataType)
                _pg2.SetPropertyReadOnly(_pg_type)
                _pg2.Append(_pg_type)

                _pg_type = wxpg.StringProperty("value ", 'obodatavalue_%s' % k, value=v.to_string())
                _pg2.SetPropertyReadOnly(_pg_type)
                _pg2.Append(_pg_type)

        return _pg_main

    def get_props(self, *args):
        pass

    def set_props(self, *args):
        pass


class ResolverCellPropsContentPanel(PropsContentPanel):
    def __init__(self, row_trans_pair, col_trans_pair, parent):
        PropsContentPanel.__init__(self, None, None, parent=parent)
        assert row_trans_pair is not None
        assert col_trans_pair is not None
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)
        self.rowTransPair = row_trans_pair
        self.colTransPair = col_trans_pair
        self._pg = self._get_prop_control()
        self.mainSizer.Add(self._pg, 1, wx.EXPAND)
        self.Layout()
        self.Fit()

    def _get_prop_control(self):
        _pg_main = wxpg.PropertyGridManager(self, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED | wxpg.PG_TOOLBAR)

        _row_wire, _row_src_node, _row_dst_node = self.rowTransPair
        _col_wire, _col_src_node, _col_dst_node = self.colTransPair

        _row_src_node_uid, _row_src_node_name = _row_src_node['uuid'], _row_src_node['nameText']
        _row_dst_node_uid, _row_dst_node_name = _row_dst_node['uuid'], _row_dst_node['nameText']
        _col_src_node_uid, _col_src_node_name = _col_src_node['uuid'], _col_src_node['nameText']
        _col_dst_node_uid, _col_dst_node_name = _col_dst_node['uuid'], _col_dst_node['nameText']

        _pg_main.Append(wxpg.PropertyCategory("TransName"))
        _pg_row_name = wxpg.StringProperty("Row",'TransNameRow', value=_row_wire['text'])
        _pg_main.SetPropertyReadOnly(_pg_row_name)
        _pg_main.Append(_pg_row_name)
        _pg_col_name = wxpg.StringProperty("Col",'TransNameCol',  value=_col_wire['text'])
        _pg_main.SetPropertyReadOnly(_pg_col_name)
        _pg_main.Append(_pg_col_name)

        _pg_main.Append(wxpg.PropertyCategory("SrcNodeUUID"))
        _pg_row_src_uuid = wxpg.StringProperty("Row",'SrcNodeUUIDRow',  value=_row_src_node_uid)
        _pg_main.SetPropertyReadOnly(_pg_row_src_uuid)
        _pg_main.Append(_pg_row_src_uuid)
        _pg_col_src_uuid = wxpg.StringProperty("Col",'SrcNodeUUIDCol', value=_col_src_node_uid)
        _pg_main.SetPropertyReadOnly(_pg_col_src_uuid)
        _pg_main.Append(_pg_col_src_uuid)

        _pg_main.Append(wxpg.PropertyCategory("SrcNodeName"))
        _pg_row_src_name = wxpg.StringProperty("Row",'SrcNodeNameRow', value=_row_src_node_name)
        _pg_main.SetPropertyReadOnly(_pg_row_src_name)
        _pg_main.Append(_pg_row_src_name)
        _pg_col_src_name = wxpg.StringProperty("Col", 'SrcNodeNameCol',value=_col_src_node_name)
        _pg_main.SetPropertyReadOnly(_pg_col_src_name)
        _pg_main.Append(_pg_col_src_name)

        _pg_main.Append(wxpg.PropertyCategory("DstNodeUUID"))
        _pg_row_dst_uuid = wxpg.StringProperty("Row",'DstNodeUUIDRow', value=_row_dst_node_uid)
        _pg_main.SetPropertyReadOnly(_pg_row_dst_uuid)
        _pg_main.Append(_pg_row_dst_uuid)
        _pg_col_dst_uuid = wxpg.StringProperty("Col",'DstNodeUUIDCol', value=_col_dst_node_uid)
        _pg_main.SetPropertyReadOnly(_pg_col_dst_uuid)
        _pg_main.Append(_pg_col_dst_uuid)

        _pg_main.Append(wxpg.PropertyCategory("DstNodeName"))
        _pg_row_dst_name = wxpg.StringProperty("Row",'DstNodeNameRow', value=_row_dst_node_name)
        _pg_main.SetPropertyReadOnly(_pg_row_dst_name)
        _pg_main.Append(_pg_row_dst_name)
        _pg_col_dst_name = wxpg.StringProperty("Col",'DstNodeNameCol', value=_col_dst_node_name)
        _pg_main.SetPropertyReadOnly(_pg_col_dst_name)
        _pg_main.Append(_pg_col_dst_name)

        return _pg_main

    def get_props(self, *args):
        pass

    def set_props(self, *args):
        pass
