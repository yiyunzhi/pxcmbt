import wx
from pubsub import pub
from gui.define_gui import EnumCanvasStyle
import yaml
from yaml import CLoader, load, dump

from application.define import EnumItemRole, EnumMBTEventType
from application.class_mbt_event import MBTEvent, MBTEventData


class MBTEventTag(yaml.YAMLObject):
    yaml_tag = '!MBTEvent'

    def __init__(self):
        pass

    def __repr__(self):
        return 'MBTEventTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _d = loader.construct_mapping(node)
        return MBTEvent(**_d)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        _mapping = [('name', data.name),
                    ('type', data.type),
                    ('readonly', data.readonly),
                    ('description', data.description),
                    ('visible', data.visible)]
        return dumper.represent_mapping(cls.yaml_tag, _mapping)


class EnumMBTEventTypeTag(yaml.YAMLObject):
    yaml_tag = '!EnumMBTEventType'

    def __init__(self):
        pass

    def __repr__(self):
        return 'NodeEventModelTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        return getattr(EnumMBTEventType, node.value)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, EnumMBTEventType(data).name)


class EnumItemRoleTag(yaml.YAMLObject):
    yaml_tag = '!EnumItemRole'

    def __init__(self):
        pass

    def __repr__(self):
        return 'NodeEventModelTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        return getattr(EnumItemRole, node.value)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, EnumItemRole(data).name)


class NodeEvtModel:
    def __init__(self):
        self.events = list()

    def get_event_names(self):
        return [x[0] for x in self.events]

    def clear(self):
        self.events.clear()

    def update(self, event_name, event_data):
        self.events.append((event_name, event_data))


class NodeEventModelTag(yaml.YAMLObject):
    yaml_tag = '!NodeEventModel'

    def __init__(self, evts):
        self.events = evts

    def __repr__(self):
        return 'NodeEventModelTag({})'.format(self.events)

    @classmethod
    def from_yaml(cls, loader, node):
        _inst = NodeEvtModel()
        for x in node.value:
            _args = [y.value for y in x.value]
            _inst.update(*_args)
        return _inst

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        # [(x, y) for x, y in data.events]
        return dumper.represent_sequence(cls.yaml_tag, [(x, y) for x, y in data.events])


yaml.add_constructor(NodeEventModelTag.yaml_tag, NodeEventModelTag.from_yaml)
yaml.add_representer(NodeEvtModel, NodeEventModelTag.to_yaml)
yaml.add_constructor(EnumItemRoleTag.yaml_tag, EnumItemRoleTag.from_yaml)
yaml.add_representer(EnumItemRole, EnumItemRoleTag.to_yaml)
yaml.add_constructor(EnumMBTEventTypeTag.yaml_tag, EnumMBTEventTypeTag.from_yaml)
yaml.add_representer(EnumMBTEventType, EnumMBTEventTypeTag.to_yaml)
yaml.add_constructor(MBTEventTag.yaml_tag, MBTEventTag.from_yaml)
yaml.add_representer(MBTEvent, MBTEventTag.to_yaml)
# _obj = NodeEvtModel()
# _obj.update('a', '0x01,0x02,0x03')
# _obj.update('b', '0x01,0x02,0x03')
# _obj.update('c', '0x01,0x02,0x03')
# _obj = EnumItemRole.ITEM_STATE
# _obj = EnumMBTEventType.OUTGOING
# pub.sendMessage(EnumMBTEventType.OUTGOING)
_obj = MBTEvent(name='c', type=EnumMBTEventType.OUTGOING)
with open('test.yaml', 'w', encoding='utf-8') as f:
    dump(_obj, f)

with open('test.yaml', 'r', encoding='utf-8') as f:
    _inst_obj = load(f, yaml.Loader)
    print(_inst_obj)
