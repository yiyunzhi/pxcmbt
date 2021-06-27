from collections import OrderedDict
from .define import *


class MBTEventData:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'None')
        self.dataType = kwargs.get('dataType', 'string')
        self.minVal = kwargs.get('minValue', 0)
        self.maxVal = kwargs.get('maxValue', 1)
        self.defaultVal = kwargs.get('default', 0)


class MBTEvent:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'None')
        self.type = kwargs.get('type', False)
        self.description = kwargs.get('description', '')
        self.readonly = kwargs.get('readonly', False)
        self.visible = kwargs.get('visible', True)
        self.data = OrderedDict()
        if kwargs.get('data') is not None:
            for x in kwargs.get('data'):
                _mbt_data = MBTEventData(**x)
                self.add_data(_mbt_data)

    def has_data(self, name):
        if name is None:
            return False
        return name in self.data

    def add_data(self, data: MBTEventData):
        if not self.has_data(data.name):
            self.data.update({data.name: data})

    def remove_data(self, name):
        if self.has_data(name):
            self.data.pop(name)

    def get_data_types(self, with_name=False):
        return [v.dataType if not with_name else (v.name, v.dataType) for k, v in self.data.items()]


class MBTEventManager:
    def __init__(self):
        self._events = dict()
        self.lastLoadPath = None

    def get_events_names(self):
        return list(self._events.keys())

    def get_all_events(self):
        return self._events

    def get_event(self, name):
        return self._events.get(name)

    def deserialize(self, data):
        if data is None:
            return
        assert 'HEADER' in data
        assert 'BODY' in data
        _body = data['BODY']
        for x in _body:
            _evt = MBTEvent(**x)
            self.register_event(_evt)

    def serialize(self):
        pass

    def get_incoming_event(self):
        return list(filter(lambda x: x.type == EnumMBTEventType.INCOMING, self._events))

    def get_outgoing_event(self):
        return list(filter(lambda x: x.type == EnumMBTEventType.OUTGOING, self._events))

    def register_event(self, event: MBTEvent):
        if event.name not in self._events:
            self._events.update({event.name: event})

    def unregister_event(self, evt_name):
        if evt_name in self._events:
            self._events.pop(evt_name)

    def has_incoming_event(self, evt_name):
        pass

    def has_outgoing_event(self, evt_name):
        pass


class NodeEvtModel:
    def __init__(self):
        self.events = list()

    def get_event_names(self):
        return [x[0] for x in self.events]

    def clear(self):
        self.events.clear()

    def update(self, event_name, event_data):
        self.events.append((event_name, event_data))