import os, wx, shutil
import wx.lib.scrolledpanel as sp
from application.class_dot_graph_generator import GvGen
from application.class_app_file_io import DotGraphImageFileIO
from application.class_app_file_io import DotGraphStringIO


class SingleCanvasDotGraphViewPanel(sp.ScrolledPanel):
    def __init__(self, parent, name, image_path=None):
        sp.ScrolledPanel.__init__(self, parent, wx.ID_ANY)
        self.SetupScrolling()
        self.name = name
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.imagePath = image_path
        self.image = wx.Image(1, 1)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.image))
        self.mainSizer.Add(self.imageCtrl, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def canvas2dot(self, stc_file_io, string_io, name=None):
        if name is None:
            name = self.name
        if stc_file_io is None:
            _gv_graph = GvGen()
            _gv_graph.dot(string_io)
        _body1 = stc_file_io.body
        _nodes1 = _body1.nodes
        _wires1 = _body1.wires

        _gv_graph = GvGen()
        _gv_graph_root1 = _gv_graph.newItem(name)
        _node_1_map = dict()
        if _nodes1 is not None:
            for x in _nodes1:
                _node = _gv_graph.newItem(x['nameText'], _gv_graph_root1)
                _node_1_map.update({x['uuid']: _node})
                _gv_graph.propertyAppend(_node, "tooltip", x['nameText'])
        if _wires1 is not None:
            for x in _wires1:
                _src_node = _node_1_map.get(x['srcNodeUUID'])
                _dst_node = _node_1_map.get(x['dstNodeUUID'])
                if _src_node is not None and _dst_node is not None:
                    _link = _gv_graph.newLink(_src_node, _dst_node)
                    _gv_graph.propertyAppend(_link, "label", x['text'])
                    # _gv_graph.propertyAppend(_link, "tooltip", x['text'])
        _gv_graph.dot(string_io)

    def show_graph(self, stc_file_io, name='A'):
        _file_io = DotGraphImageFileIO(self.name)
        _dot_graph_string_io = DotGraphStringIO()
        self.canvas2dot(stc_file_io, _dot_graph_string_io, name)
        _image_path = _file_io.write(_dot_graph_string_io.content)
        self.load_image(_image_path)

    def load_image(self, path):
        _img = wx.Image(path, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        _w = _img.GetWidth()
        _h = _img.GetHeight()
        self.imageCtrl.SetBitmap(wx.Bitmap(_img))
        self.Refresh()


class CompoundCanvasDotGraphViewPanel(sp.ScrolledPanel):
    def __init__(self, parent, name, image_path=None):
        sp.ScrolledPanel.__init__(self, parent, wx.ID_ANY)
        self.SetupScrolling()
        self.name = name
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.imagePath = image_path
        self.image = wx.Image(1, 1)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.image))
        # bind events
        self.imageCtrl.Bind(wx.EVT_CONTEXT_MENU, self.on_image_context_menu)
        # layout
        self.mainSizer.Add(self.imageCtrl, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def on_image_context_menu(self, evt):
        _menu = wx.Menu()
        _save_as_img_id = wx.NewIdRef()
        _menu.Append(_save_as_img_id, "SaveAsImage")
        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.Bind(wx.EVT_MENU, self.on_cm_save_as_image, id=_save_as_img_id)
        self.PopupMenu(_menu)
        _menu.Destroy()

    def on_cm_save_as_image(self, evt):
        _dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard="PNG files (*.png)|*.png", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        _dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if _dlg.ShowModal() == wx.ID_OK:
            _path = _dlg.GetPath()
            shutil.copyfile(self.imagePath, _path)

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
                    # _gv_graph.propertyAppend(_link, "tooltip", x['text'])
        if _wires2 is not None:
            for x in _wires2:
                _src_node = _node_2_map.get(x['srcNodeUUID'])
                _dst_node = _node_2_map.get(x['dstNodeUUID'])
                if _src_node is not None and _dst_node is not None:
                    _link = _gv_graph.newLink(_src_node, _dst_node)
                    _gv_graph.propertyAppend(_link, "label", x['text'])
        _gv_graph.dot(string_io)

    def show_graph(self, a_stc_file_io, b_stc_file_io, a_name='A', b_name='B'):
        _file_io = DotGraphImageFileIO(self.name)
        _dot_graph_string_io = DotGraphStringIO()
        self.merge_canvas2dot(a_stc_file_io, b_stc_file_io, _dot_graph_string_io, a_name, b_name)
        _image_path = _file_io.write(_dot_graph_string_io.content)
        self.imagePath = _image_path
        self.load_image(_image_path)

    def load_image(self, path):
        _img = wx.Image(path, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        _w = _img.GetWidth()
        _h = _img.GetHeight()
        self.imageCtrl.SetBitmap(wx.Bitmap(_img))
        self.SetSize(_w, _h)
        self.Refresh()
