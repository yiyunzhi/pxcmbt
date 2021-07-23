from application.class_yaml_tag import *
from application.class_app_file_io import ApplicationStcFileIO
from application.utils_helper import util_get_uuid_string

_replaced = dict()
_file_io = ApplicationStcFileIO('application/data/feature_libs/PWR/', 'PWR.stc')
_file_io.read()
_body = _file_io.body
_nodes = _body.nodes
_wires = _body.wires
for x in _nodes:
    _old_uuid = x['uuid']
    _new_uuid = util_get_uuid_string()
    _replaced.update({_old_uuid: _new_uuid})
    x['uuid'] = _new_uuid
for x in _wires:
    _old_uuid = x['uuid']
    _old_src_node_uuid = x['srcNodeUUID']
    _old_dst_node_uuid = x['dstNodeUUID']
    if _old_uuid in _replaced:
        _new_uuid = _replaced[_old_uuid]
    else:
        _new_uuid = util_get_uuid_string()
    if _old_src_node_uuid in _replaced:
        _new_src_node_uuid = _replaced[_old_src_node_uuid]
    else:
        _new_src_node_uuid = util_get_uuid_string()
    if _old_dst_node_uuid in _replaced:
        _new_dst_node_uuid = _replaced[_old_dst_node_uuid]
    else:
        _new_dst_node_uuid = util_get_uuid_string()
    x['uuid'] = _new_uuid
    x['srcNodeUUID'] = _new_src_node_uuid
    x['dstNodeUUID'] = _new_dst_node_uuid

_file_io.filePath = 'application/data/feature_libs/'
_file_io.write({'canvas': _body.canvas, 'nodes': _nodes, 'wires': _wires})
# _replaced = dict()
# with open('application/data/feature_libs/PWR/PWR.stc') as f:
#     _line = f.readline()
#     while _line:
#         _s = _line.find('uuid:')
#         if _s is not None:
#             _replaced.update({_s: _s})
#         _line = f.readline()
# print(_replaced)
print(_file_io)
