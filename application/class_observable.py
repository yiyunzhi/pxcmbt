# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : Test Control System
# Sourcefile(s) : class_observable.py
# ------------------------------------------------------------------------------
#
# File          : class_observable.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from collections import OrderedDict
from .define import EnumOBOType, EnumOBODataType


class ObservableData:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'None')
        self.dataType = kwargs.get('dataType', 'string')
        self.defaultVal = kwargs.get('default', '')

    def to_string(self):
        if self.dataType == EnumOBODataType.INTEGER.value:
            return '%d' % self.defaultVal
        elif self.dataType == EnumOBODataType.HEX.value:
            return '0x%X' % self.defaultVal
        else:
            return '%s' % self.defaultVal

    def from_string(self, data):
        if self.dataType == EnumOBODataType.INTEGER.value:
            self.dataType = int(data)
        elif self.dataType == EnumOBODataType.HEX.value:
            self.defaultVal = int(data)
        else:
            self.defaultVal = data


class Observable:
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def __eq__(self, other):
        return (other.name == self.name
                and self.uuid == other.uuid
                and self.type == other.type
                and self.visible == other.visible
                and self.readonly == other.readonly
                and self.description == other.description
                and self.data == other.data)

    def attach_default_data(self):
        if self.type == EnumOBOType.LED.value:
            _l = [ObservableData(name='label', dataType=EnumOBODataType.STRING.value, default='LED'),
                  ObservableData(name='state', dataType=EnumOBODataType.INTEGER.value, default=0x0),
                  ObservableData(name='color', dataType=EnumOBODataType.INTEGER.value, default=0x000000),
                  ObservableData(name='flash', dataType=EnumOBODataType.INTEGER.value, default=0x00000000)
                  ]
        elif self.type == EnumOBOType.DIAGNOSIS.value:
            _l = [ObservableData(name='code', dataType=EnumOBODataType.INTEGER.value, default=0x0000),
                  ObservableData(name='priority', dataType=EnumOBODataType.INTEGER.value, default=0x0000),
                  ObservableData(name='location', dataType=EnumOBODataType.INTEGER.value, default=0x0000),
                  ObservableData(name='addValue', dataType=EnumOBODataType.INTEGER.value, default=0x0000)
                  ]
        elif self.type == EnumOBOType.FHOST_SB.value:
            _l = [ObservableData(name='value', dataType=EnumOBODataType.INTEGER.value, default=0x00),
                  ObservableData(name='offset', dataType=EnumOBODataType.INTEGER.value, default=0x00),
                  ObservableData(name='bitLength', dataType=EnumOBODataType.INTEGER.value, default=0x08),
                  ObservableData(name='mask', dataType=EnumOBODataType.INTEGER.value, default=0xEF)
                  ]
        elif self.type == EnumOBOType.PD.value:
            _l = [ObservableData(name='value', dataType=EnumOBODataType.INTEGER.value, default=0x00),
                  ObservableData(name='offset', dataType=EnumOBODataType.INTEGER.value, default=0x00),
                  ObservableData(name='bitLength', dataType=EnumOBODataType.INTEGER.value, default=0x08),
                  ObservableData(name='mask', dataType=EnumOBODataType.INTEGER.value, default=0xFF)
                  ]
        elif self.type == EnumOBOType.FDEVICE_SB.value:
            _l = [ObservableData(name='value', dataType=EnumOBODataType.INTEGER.value, default=0x00),
                  ObservableData(name='offset', dataType=EnumOBODataType.INTEGER.value, default=0x00),
                  ObservableData(name='bitLength', dataType=EnumOBODataType.INTEGER.value, default=0x08),
                  ObservableData(name='mask', dataType=EnumOBODataType.INTEGER.value, default=0xEF)
                  ]
        else:
            _l = None
        if _l is not None:
            [self.add_data(x) for x in _l]

    def update(self, **kwargs):
        if kwargs.get('uuid'): self.uuid = kwargs.get('uuid')
        if kwargs.get('name'): self.name = kwargs.get('name')
        if kwargs.get('type'): self.type = kwargs.get('type')
        if kwargs.get('description'): self.description = kwargs.get('description')
        self.readonly = kwargs.get('readonly', False)
        self.visible = kwargs.get('visible', True)
        self.data = OrderedDict()
        _data = kwargs.get('data')
        if _data is None:
            return
        if isinstance(_data, OrderedDict):
            self.data = _data
        elif isinstance(_data, list):
            for x in _data:
                _mbt_data = ObservableData(**x)
                self.add_data(_mbt_data)

    def has_data(self, data_name):
        if data_name is None:
            return False
        return data_name in self.data

    def add_data(self, data: ObservableData):
        if not self.has_data(data.name):
            self.data.update({data.name: data})

    def remove_data(self, name):
        if self.has_data(name):
            self.data.pop(name)

    def get_data_types(self, with_name=False):
        return [v.dataType if not with_name else (v.name, v.dataType) for k, v in self.data.items()]

    def get_data_in_string(self):
        if self.data is not None:
            return ','.join([v.to_string() for k, v in self.data.items()])
        else:
            return ''

    def set_data_from_string(self, string):
        if string != '':
            _data_str_lst = string.split(',')
            _data_lst = list(self.data.values())
            for idx, x in enumerate(_data_str_lst):
                if idx < len(_data_lst):
                    _data = _data_lst[idx]
                    _data.from_string(x)


class MBTOBOManager:
    def __init__(self):
        self._obos = dict()

    def update(self, obo):
        _obo = self._obos.get(obo.uuid)
        if _obo is not None:
            _obo.type = obo.type
            _obo.description = obo.description
            _obo.visible = obo.visible
            _obo.readonly = obo.readonly
            _obo.data = obo.data

    def clear(self):
        self._obos.clear()

    def get_obos_names(self):
        return [v.name for k, v in self._obos.items()]

    def get_obos_names_by_type(self, type_lst):
        return [v.name for k, v in self._obos.items() if v.type in type_lst]

    def get_all_obos(self):
        return self._obos

    def get_obos_by_type(self, type_lst):
        return [v for k, v in self._obos.items() if v.type in type_lst]

    def get_obo(self, uuid):
        return self._obos.get(uuid)

    def get_obo_by_name(self, name):
        for k, v in self._obos.items():
            if v.name == name:
                return v

    def is_obo_changed(self, _obo):
        _obo = self._obos.get(_obo.uuid)
        return _obo != _obo

    def deserialize(self, data):
        if data is None:
            return
        if not hasattr(data, 'body'):
            return
        _evts = data.body.obos
        for k, v in _evts.items():
            self.register_obo(v)

    def has_obo(self, obo_uuid):
        return obo_uuid in self._obos

    def serialize(self):
        pass

    def register_obo(self, obo):
        if obo.uuid not in self._obos:
            self._obos.update({obo.uuid: obo})

    def register_obos(self, obos: [dict, list]):
        if isinstance(obos, dict):
            for k, v in obos.items():
                if isinstance(v, Observable):
                    self.register_obo(v)
        elif isinstance(obos, list):
            for k in obos:
                if isinstance(k, Observable):
                    self.register_obo(k)

    def unregister_obo(self, obo_uuid):
        if obo_uuid in self._obos:
            self._obos.pop(obo_uuid)
