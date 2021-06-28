from collections import OrderedDict
from .define import *


class MBTEventData:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'None')
        self.dataType = kwargs.get('dataType', 'string')
        self.defaultVal = kwargs.get('default', '')


class MBTEvent:
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def __eq__(self, other):
        return (other.name == self.name
                and self.type == other.type
                and self.visible == other.visible
                and self.readonly == other.readonly
                and self.description == other.description
                and self.data == other.data)

    def update(self, **kwargs):
        self.name = kwargs.get('name', 'None')
        self.type = kwargs.get('type', EnumMBTEventType.OUTGOING.value)
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

    def update(self, event):
        _evt = self._events.get(event.name)
        _evt.name = event.name
        _evt.type = event.type
        _evt.description = event.description
        _evt.visible = event.visible
        _evt.readonly = event.readonly
        _evt.data = event.data

    def get_events_names(self):
        return list(self._events.keys())

    def get_all_events(self):
        return self._events

    def get_event(self, name):
        return self._events.get(name)

    def is_event_changed(self, event):
        _evt = self._events.get(event.name)
        return _evt != event

    def deserialize(self, data):
        if data is None:
            return
        assert 'HEADER' in data
        assert 'BODY' in data
        _body = data['BODY']
        for x in _body:
            if isinstance(x, dict):
                _evt = MBTEvent(**x)
            elif isinstance(x, MBTEvent):
                _evt = x
            else:
                continue
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

    def has_event(self, evt_name):
        return evt_name in self._events


class NodeEvtModel:
    def __init__(self):
        self.events = list()

    def get_event_names(self):
        return [x[0] for x in self.events]

    def clear(self):
        self.events.clear()

    def update(self, event_name, event_data):
        self.events.append((event_name, event_data))
