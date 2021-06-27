import yaml
from .class_mbt_event import NodeEvtModel, MBTEvent
from .define import EnumItemRole, EnumMBTEventType


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
yaml.add_constructor(EnumItemRoleTag.yaml_tag, EnumItemRoleTag.from_yaml)
yaml.add_representer(EnumItemRole, EnumItemRoleTag.to_yaml)
yaml.add_constructor(EnumMBTEventTypeTag.yaml_tag, EnumMBTEventTypeTag.from_yaml)
yaml.add_representer(EnumMBTEventType, EnumMBTEventTypeTag.to_yaml)
yaml.add_constructor(MBTEventTag.yaml_tag, MBTEventTag.from_yaml)
yaml.add_representer(MBTEvent, MBTEventTag.to_yaml)
