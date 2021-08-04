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


class Observable:
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def __eq__(self, other):
        return (other.name == self.name
                and self.type == other.type
                and self.visible == other.visible
                and self.readonly == other.readonly
                and self.description == other.description
                and self.data == other.data)

    def attach_default_data(self):
        if self.type == EnumOBOType.LED.value:
            _l = [ObservableData(name='state', dataType=EnumOBODataType.INTEGER.value, default=0),
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
            _l = [ObservableData(name='value', dataType=EnumOBODataType.INTEGER.value, default=0x00)
                  ]
        elif self.type == EnumOBOType.PD.value:
            _l = [ObservableData(name='value', dataType=EnumOBODataType.INTEGER.value, default=0x00)
                  ]
        elif self.type == EnumOBOType.FDEVICE_SB.value:
            _l = [ObservableData(name='value', dataType=EnumOBODataType.INTEGER.value, default=0x00)
                  ]
        else:
            _l = None
        if _l is not None:
            [self.add_data(x) for x in _l]

    def update(self, **kwargs):
        self.name = kwargs.get('name', 'None')
        self.type = kwargs.get('type', 'LED')
        self.description = kwargs.get('description', '')
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

    def has_data(self, name):
        if name is None:
            return False
        return name in self.data

    def add_data(self, data: ObservableData):
        if not self.has_data(data.name):
            self.data.update({data.name: data})

    def remove_data(self, name):
        if self.has_data(name):
            self.data.pop(name)

    def get_data_types(self, with_name=False):
        return [v.dataType if not with_name else (v.name, v.dataType) for k, v in self.data.items()]


class MBTOBOManager:
    def __init__(self):
        self._obos = dict()

    def update(self, event):
        _obo = self._obos.get(event.name)
        _obo.type = event.type
        _obo.description = event.description
        _obo.visible = event.visible
        _obo.readonly = event.readonly
        _obo.data = event.data

    def get_events_names(self):
        return list(self._obos.keys())

    def get_all_obos(self):
        return self._obos

    def get_obo(self, name):
        return self._obos.get(name)

    def is_obo_changed(self, _obo):
        _obo = self._obos.get(_obo.name)
        return _obo != _obo

    def deserialize(self, data):
        if data is None:
            return
        if not hasattr(data, 'body'):
            return
        _evts = data.body.events
        for k, v in _evts.items():
            self.register_obo(v)

    def has_obo(self, obo_name):
        return obo_name in self._obos

    def serialize(self):
        pass

    def register_obo(self, obo):
        if obo.name not in self._obos:
            self._obos.update({obo.name: obo})

    def unregister_obo(self, obo_name):
        if obo_name in self._obos:
            self._obos.pop(obo_name)
