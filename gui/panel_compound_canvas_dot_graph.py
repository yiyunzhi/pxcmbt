import wx
import wx.html2
from application.class_dot_graph_generator import GvGen
from application.class_app_file_io import DotGraphHtmlFileIO


class CompoundCanvasDotGraphViewPanel(wx.Panel):
    def __init__(self, parent, wx_id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, wx_id)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        wx.html2.WebView.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE10)
        self.browser = wx.html2.WebView.New(self)
        self.mainSizer.Add(self.browser, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def merge_canvas2dot(self, canvas1_file_io, canvas2_file_io, string_io, a_name='A', b_name='B'):
        if canvas1_file_io is None or canvas2_file_io is None:
            _gv_graph = GvGen()
            _gv_graph.dot(string_io)
        _body1 = canvas1_file_io.body
        _nodes1 = _body1.nodes
        _wires1 = _body1.wires
        _body2 = canvas2_file_io.body
        _nodes2 = _body2.nodes
        _wires2 = _body2.wires
        _gv_graph = GvGen()
        _gv_graph_root1 = _gv_graph.newItem(a_name)
        _gv_graph_root2 = _gv_graph.newItem(b_name)
        _node_1_map = dict()
        _node_2_map = dict()
        if _nodes1 is not None:
            for x in _nodes1:
                _node = _gv_graph.newItem(x['nameText'], _gv_graph_root1)
                _node_1_map.update({x['uuid']: _node})
                _gv_graph.propertyAppend(_node, "tooltip", x['nameText'])
        if _nodes2 is not None:
            for x in _nodes2:
                _node = _gv_graph.newItem(x['nameText'], _gv_graph_root2)
                _node_2_map.update({x['uuid']: _node})
                _gv_graph.propertyAppend(_node, "tooltip", x['nameText'])
        if _wires1 is not None:
            for x in _wires1:
                _src_node = _node_1_map.get(x['srcNodeUUID'])
                _dst_node = _node_1_map.get(x['dstNodeUUID'])
                if _src_node is not None and _dst_node is not None:
                    _link = _gv_graph.newLink(_src_node, _dst_node)
                    _gv_graph.propertyAppend(_link, "label", x['text'])
                    #_gv_graph.propertyAppend(_link, "tooltip", x['text'])
        if _wires2 is not None:
            for x in _wires2:
                _src_node = _node_2_map.get(x['srcNodeUUID'])
                _dst_node = _node_2_map.get(x['dstNodeUUID'])
                if _src_node is not None and _dst_node is not None:
                    _link = _gv_graph.newLink(_src_node, _dst_node)
                    _gv_graph.propertyAppend(_link, "label", x['text'])
        _gv_graph.dot(string_io)

    def show_graph(self, a_stc_file_io, b_stc_file_io, a_name='A', b_name='B'):
        _file_io = DotGraphHtmlFileIO()
        _file_io.read()
        self.merge_canvas2dot(a_stc_file_io, b_stc_file_io, _file_io.dotGraphStringIO, a_name, b_name)
        _html_path = _file_io.update_dot_graph()
        self.show_html_from_file(_html_path)

    def show_html(self, html):
        self.browser.SetPage(html, '')

    def show_html_from_url(self, url):
        self.browser.LoadURL(url)

    def show_html_from_file(self, file_path):
        self.browser.LoadURL(wx.FileSystem.FileNameToURL(file_path))
