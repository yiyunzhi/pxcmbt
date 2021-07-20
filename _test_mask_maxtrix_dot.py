import os
from distutils.version import LooseVersion
import wx
import wx.html2
import wx.lib.mixins.inspection
from application.define import APP_NAME, REQ_WX_VERSION_STRING

from application.class_yaml_tag import *
from application.class_dot_graph_generator import GvGen
from application.class_project import Project
from application.class_app_setting import APP_SETTING
from application.define import EnumItemRole
from application.class_app_file_io import ApplicationStcFileIO, DotGraphHtmlFileIO

_root_stc_uuid = '179f36b1e4a941019c91689ba33adf0e'
_uf_stc_uuid = '947a06d84a6543c9be1269caaa5fa354'
_proj = Project('test')
_root_stc_file_io = _proj.get_file_io(_root_stc_uuid, EnumItemRole.DEV_FEATURE_STATE)
_uf_stc_file_io = _proj.get_file_io(_uf_stc_uuid, EnumItemRole.USER_FEATURE_STATE)


class CompoundCanvasDotGraphViewPanel(wx.Panel):
    def __init__(self, parent, wx_id=wx.ID_ANY, canvas1_name='A', canvas2_name='B'):
        wx.Panel.__init__(self, parent, wx_id)
        self.canvas1Name = canvas1_name
        self.canvas2Name = canvas2_name
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        wx.html2.WebView.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE10)
        self.browser = wx.html2.WebView.New(self)
        self.testBtn = wx.Button(self, wx.ID_ANY, 'TEST')
        self.mainSizer.Add(self.browser, 1, wx.EXPAND)
        self.mainSizer.Add(self.testBtn, 0, wx.EXPAND)
        self.testBtn.Bind(wx.EVT_BUTTON, self.on_test_clicked)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def merge_canvas2dot(self, canvas1_file_io, canvas2_file_io, string_io):
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
        _gv_graph_root1 = _gv_graph.newItem(self.canvas1Name)
        _gv_graph_root2 = _gv_graph.newItem(self.canvas2Name)
        _node_1_map = dict()
        _node_2_map = dict()
        for x in _nodes1:
            _node = _gv_graph.newItem(x['nameText'], _gv_graph_root1)
            _node_1_map.update({x['uuid']: _node})
        for x in _nodes2:
            _node = _gv_graph.newItem(x['nameText'], _gv_graph_root2)
            _node_2_map.update({x['uuid']: _node})
        for x in _wires1:
            _src_node = _node_1_map.get(x['srcNodeUUID'])
            _dst_node = _node_1_map.get(x['dstNodeUUID'])
            if _src_node is not None and _dst_node is not None:
                _link = _gv_graph.newLink(_src_node, _dst_node)
                _gv_graph.propertyAppend(_link, "label", x['text'])
        for x in _wires2:
            _src_node = _node_2_map.get(x['srcNodeUUID'])
            _dst_node = _node_2_map.get(x['dstNodeUUID'])
            if _src_node is not None and _dst_node is not None:
                _link = _gv_graph.newLink(_src_node, _dst_node)
                _gv_graph.propertyAppend(_link, "label", x['text'])
        _gv_graph.dot(string_io)

    def on_test_clicked(self, evt):
        _file_io = DotGraphHtmlFileIO()
        _file_io.read()
        self.merge_canvas2dot(_uf_stc_file_io, _root_stc_file_io, _file_io.dotGraphStringIO)
        _html_path = _file_io.update_dot_graph()
        self.show_html_from_file(_html_path)

    def show_html(self, html):
        self.browser.SetPage(html, '')

    def show_html_from_url(self, url):
        self.browser.LoadURL(url)

    def show_html_from_file(self, file_path):
        self.browser.LoadURL(wx.FileSystem.FileNameToURL(file_path))


class AppFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.compoundCanvasDotGraphViewPanel = CompoundCanvasDotGraphViewPanel(self)
        self.mainSizer.Add(self.compoundCanvasDotGraphViewPanel, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()


class App(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        if LooseVersion(REQ_WX_VERSION_STRING) != LooseVersion(wx.VERSION_STRING):
            wx.MessageBox(caption="Warning",
                          message="You're using version %s of wxPython, but this copy of the demo was written for version %s.\n"
                                  "There may be some version incompatibilities..."
                                  % (wx.VERSION_STRING, REQ_WX_VERSION_STRING))

        self.InitInspection()  # for the InspectionMixin base class
        wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
        self.SetAppName(APP_NAME)
        # Create and show the splash screen.  It will then create and
        # show the main frame when it is time to do so.  Normally when
        # using a SplashScreen you would create it, show it and then
        # continue on with the application's initialization, finally
        # creating and showing the main application window(s).  In
        # this case we have nothing else to do so we'll delay showing
        # the main frame until later (see ShowMain above) so the users
        # can see the SplashScreen effect.
        # _splash = GuiSplashScreen()
        # _splash.Show()
        _main_frm = AppFrame(None)
        _main_frm.Show()
        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
