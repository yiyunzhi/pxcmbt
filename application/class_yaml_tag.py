import yaml
from .class_mbt_event import NodeEvtModel
from .define import EnumItemRole, EnumMBTEventType


class EnumItemRoleTag(yaml.YAMLObject):
    yaml_tag = '!EnumItemRole'

    def __init__(self):
        pass

    def __repr__(self):
        return 'NodeEventModelTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _inst = NodeEvtModel()
        for x in node.value:
            _args = [y.value for y in x.value]
            _inst.update(*_args)
        return _inst

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data)


class NodeEventModelTag(yaml.YAMLObject):
    yaml_tag = '!NodeEventModel'

    def __init__(self):
        pass

    def __repr__(self):
        return 'NodeEventModelTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _inst = NodeEvtModel()
        for x in node.value:
            _args = [y.value for y in x.value]
            _inst.update(*_args)
        return _inst

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        return dumper.represent_sequence(cls.yaml_tag, [(x, y) for x, y in data.events])


yaml.add_constructor(NodeEventModelTag.yaml_tag, NodeEventModelTag.from_yaml)
yaml.add_representer(NodeEvtModel, NodeEventModelTag.to_yaml)
