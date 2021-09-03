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
                and self.uuid == other.uuid
                and self.type == other.type
                and self.visible == other.visible
                and self.readonly == other.readonly
                and self.description == other.description
                and self.data == other.data)

    def update(self, **kwargs):
        if kwargs.get('uuid'): self.uuid = kwargs.get('uuid')
        if kwargs.get('name'): self.name = kwargs.get('name')
        if kwargs.get('type'): self.type = kwargs.get('type')
        if kwargs.get('description'): self.description = kwargs.get('description')
        self.readonly = kwargs.get('readonly', False)
        self.visible = kwargs.get('visible', True)
        self.data = dict()
        _data = kwargs.get('data')
        if _data is None:
            return
        if isinstance(_data, dict) or isinstance(_data, OrderedDict):
            self.data = _data
        elif isinstance(_data, list):
            for x in _data:
                _mbt_data = MBTEventData(**x)
                self.add_data(_mbt_data)

    def has_data(self, data_name):
        if data_name is None:
            return False
        return data_name in self.data

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
        _evt = self._events.get(event.uuid)
        if _evt is not None:
            _evt.name = event.name
            _evt.type = event.type
            _evt.description = event.description
            _evt.visible = event.visible
            _evt.readonly = event.readonly
            _evt.data = event.data

    def get_events_names(self):
        return [v.name for k, v in self._events.items()]

    def get_events_names_by_type(self, type_lst):
        return [v.name for k, v in self._events.items() if v.type in type_lst]

    def get_all_events(self):
        return self._events

    def get_event(self, uuid):
        return self._events.get(uuid)

    def is_event_changed(self, event):
        _evt = self._events.get(event.uuid)
        return _evt != event

    def deserialize(self, data):
        if data is None:
            return
        if not hasattr(data, 'body'):
            return
        _evts = data.body.events
        for k, v in _evts.items():
            self.register_event(v)

    def serialize(self):
        pass

    def get_incoming_event(self):
        return list(filter(lambda x: x.type == EnumMBTEventType.INCOMING, self._events))

    def get_outgoing_event(self):
        return list(filter(lambda x: x.type == EnumMBTEventType.OUTGOING, self._events))

    def register_event(self, event: MBTEvent):
        if event.uuid not in self._events:
            self._events.update({event.uuid: event})

    def register_events(self, events: [dict, list]):
        if isinstance(events, dict):
            for k, v in events.items():
                if isinstance(v, MBTEvent):
                    self.register_event(v)
        elif isinstance(events, list):
            for k in events:
                if isinstance(k, MBTEvent):
                    self.register_event(k)

    def unregister_event(self, evt_uuid):
        if evt_uuid in self._events:
            self._events.pop(evt_uuid)

    def has_event(self, evt_uuid):
        return evt_uuid in self._events


class NodeEvtModel:
    def __init__(self):
        self.events = list()

    def get_event_names(self):
        return [x[0] for x in self.events]

    def clear(self):
        self.events.clear()

    def update(self, event_name, event_data):
        self.events.append((event_name, event_data))
