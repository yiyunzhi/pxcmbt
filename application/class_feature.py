from .define import EnumItemRole


class _PARAOBJ:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Feature:
    def __init__(self, name, project, stc_uid, evt_uid, rsv_uid=None, obo_uid=None):
        self.name = name
        self.project = project
        self.stcUID = stc_uid
        self.evtUID = evt_uid
        self.rsvUID = rsv_uid
        self.oboUID = obo_uid
        self.states = dict()
        self.events = dict()
        self.transitions = dict()
        self.resolvers = dict()
        self.obos = dict()
        self.stcFileIO = self.project.get_file_io(stc_uid, EnumItemRole.DEV_FEATURE_STATE)
        if self.stcFileIO is not None:
            self.stcFileIO.read()
            self._parse_states()
            self._parse_transitions()
        self.evtFileIO = self.project.get_file_io(evt_uid, EnumItemRole.DEV_FEATURE_EVENT)
        if self.evtFileIO is not None:
            self.evtFileIO.read()
            self._parse_events()
        if rsv_uid is not None:
            self.rsvFileIO = self.project.get_file_io(rsv_uid, EnumItemRole.USER_FEATURE_RESOLVER)
        else:
            self.rsvFileIO = None
        if self.rsvFileIO is not None:
            self.rsvFileIO.read()
            self._parse_resolvers()
        if obo_uid is not None:
            self.oboFileIO = self.project.get_file_io(obo_uid, EnumItemRole.DEV_FEATURE_OBO)
        else:
            self.oboFileIO = None
        if self.oboFileIO is not None:
            self.oboFileIO.read()
            self._parse_obos()

    def _parse_states(self):
        if self.stcFileIO is not None:
            _nodes = self.stcFileIO.body.nodes
            if _nodes is not None:
                for x in _nodes:
                    _obj = _PARAOBJ(**x)
                    self.states.update({_obj.uuid: _obj})

    def _parse_transitions(self):
        if self.stcFileIO is not None:
            _wires = self.stcFileIO.body.wires
            if _wires is not None:
                for x in _wires:
                    _obj = _PARAOBJ(**x)
                    self.transitions.update({_obj.uuid: _obj})

    def _parse_events(self):
        if self.evtFileIO is not None:
            _events = self.evtFileIO.body.events
            if _events is not None:
                for k, v in _events.items():
                    self.events.update({v.uuid: v})

    def _parse_resolvers(self):
        if self.rsvFileIO is not None:
            _rsv = self.rsvFileIO.body.rsv
            if _rsv is not None:
                pass
            # for k,v in _rsv.items():
            #     _obj = _PARAOBJ(**v)
            #     self.resolvers.update({_obj.uuid: _obj})

    def _parse_obos(self):
        if self.oboFileIO is not None:
            _obos = self.oboFileIO.body.obos
            if _obos is not None:
                for k, v in _obos.items():
                    self.obos.update({v.uuid: v})
