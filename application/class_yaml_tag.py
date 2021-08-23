import yaml
from .class_mbt_event import NodeEvtModel, MBTEvent,MBTEventData
from .class_observable import ObservableData,Observable
from .define import EnumItemRole, EnumMBTEventType, StandardItemData,EnumOBOType,EnumOBODataType


class StandardItemDataTag(yaml.YAMLObject):
    yaml_tag = '!StandardItemData'

    def __init__(self):
        pass

    def __repr__(self):
        return 'StandardItemDataTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _d = loader.construct_mapping(node)
        _inst = StandardItemData()
        for k, v in _d.items():
            setattr(_inst, k, v)
        return _inst

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        _mapping = list()
        for x in data.__slots__:
            _mapping.append((x, getattr(data, x)))
        return dumper.represent_mapping(cls.yaml_tag, _mapping)


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
                    ('uuid', data.uuid),
                    ('type', data.type),
                    ('readonly', data.readonly),
                    ('description', data.description),
                    ('visible', data.visible),
                    ('data', data.data)]
        return dumper.represent_mapping(cls.yaml_tag, _mapping)


class MBTEventDataTag(yaml.YAMLObject):
    yaml_tag = '!MBTEventData'

    def __init__(self):
        pass

    def __repr__(self):
        return 'MBTEventDataTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _d = loader.construct_mapping(node)
        return MBTEventData(**_d)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        _mapping = [('name', data.name),
                    ('dataType', data.dataType),
                    ('default', data.defaultVal),
                   ]
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



class MBTOboTag(yaml.YAMLObject):
    yaml_tag = '!MBTObo'

    def __init__(self):
        pass

    def __repr__(self):
        return 'MBTOboTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _d = loader.construct_mapping(node)
        return Observable(**_d)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        _mapping = [('name', data.name),
                    ('uuid', data.uuid),
                    ('type', data.type),
                    ('readonly', data.readonly),
                    ('description', data.description),
                    ('visible', data.visible),
                    ('data', data.data)]
        return dumper.represent_mapping(cls.yaml_tag, _mapping)


class MBTOboDataTag(yaml.YAMLObject):
    yaml_tag = '!MBTOboData'

    def __init__(self):
        pass

    def __repr__(self):
        return 'MBTOboDataTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        _d = loader.construct_mapping(node)
        return ObservableData(**_d)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        _mapping = [('name', data.name),
                    ('dataType', data.dataType),
                    ('default', data.defaultVal),
                   ]
        return dumper.represent_mapping(cls.yaml_tag, _mapping)


class EnumMBTOboTypeTag(yaml.YAMLObject):
    yaml_tag = '!EnumMBTOboType'

    def __init__(self):
        pass

    def __repr__(self):
        return 'EnumMBTOboTypeTag'.format()

    @classmethod
    def from_yaml(cls, loader, node):
        return getattr(EnumOBOType, node.value)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, EnumOBOType(data).name)


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

yaml.add_constructor(MBTEventDataTag.yaml_tag, MBTEventDataTag.from_yaml)
yaml.add_representer(MBTEventData, MBTEventDataTag.to_yaml)

yaml.add_constructor(StandardItemDataTag.yaml_tag, StandardItemDataTag.from_yaml)
yaml.add_representer(StandardItemData, StandardItemDataTag.to_yaml)

yaml.add_constructor(MBTOboTag.yaml_tag, MBTOboTag.from_yaml)
yaml.add_representer(Observable, MBTOboTag.to_yaml)

yaml.add_constructor(MBTOboDataTag.yaml_tag, MBTOboDataTag.from_yaml)
yaml.add_representer(ObservableData, MBTOboDataTag.to_yaml)

yaml.add_constructor(EnumMBTOboTypeTag.yaml_tag, EnumMBTOboTypeTag.from_yaml)
yaml.add_representer(EnumOBOType, EnumMBTOboTypeTag.to_yaml)