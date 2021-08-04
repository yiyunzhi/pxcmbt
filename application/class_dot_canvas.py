# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : Test Control System
# Sourcefile(s) : class_dotcanvas.py
# ------------------------------------------------------------------------------
#
# File          : class_dotcanvas.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from .class_dot_graph_generator import GvGen
from .class_app_file_io import DotGraphStringIO


class DotCanvas:
    def __init__(self, name):
        self.name = name
        self.dotStrIO = DotGraphStringIO()

    def canvas2dot(self, stc_file_io, name=None):
        self.dotStrIO.clear()
        if name is None:
            name = self.name
        if stc_file_io is None:
            _gv_graph = GvGen()
            _gv_graph.dot(self.dotStrIO)
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
        _gv_graph.dot(self.dotStrIO)
        return self.dotStrIO.content
