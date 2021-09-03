import urllib.parse
from collections import OrderedDict
from .define import EnumItemRole


class _PARAOBJ:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, OrderedDict):
                # make it pickelable
                _v = dict(v)
            else:
                _v = v
            setattr(self, k, _v)


class Feature:
    def __init__(self, name, uuid, project, root_feature, stc_uid, evt_uid, rsv_uid=None, obo_uid=None):
        self.name = name
        self.uuid = uuid
        self.rootFeature = root_feature
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
                for k, v in _rsv.items():
                    _l = list()
                    if v:
                        for kk, vv in v.items():
                            vv.data = dict(vv.data)
                            _l.append(vv)
                    self.resolvers.update({k: _l})

    def _parse_obos(self):
        if self.oboFileIO is not None:
            _obos = self.oboFileIO.body.obos
            if _obos is not None:
                for k, v in _obos.items():
                    _l = list()
                    if v:
                        for kk, vv in v.items():
                            vv.data = dict(vv.data)
                            _l.append(vv)
                    self.obos.update({v.uuid: _l})

    def __iter__(self):
        # todo: sequence started from INIT_STATE
        # iteration all transitions
        for trans_uuid, trans in self.transitions.items():
            _i = 0
            _src_node_uuid = trans.srcNodeUUID
            _dst_node_uuid = trans.dstNodeUUID
            _src_node = self.states.get(_src_node_uuid)
            _dst_node = self.states.get(_dst_node_uuid)
            _f_enter_event = _dst_node.enterEventModel.events if hasattr(_dst_node,
                                                                         'enterEventModel') else None
            _f_exit_event = _src_node.exitEventModel.events if hasattr(_src_node,
                                                                       'exitEventModel') else None
            for root_trans_uuid, root_trans in self.rootFeature.transitions.items():
                _resolver_id = '%s_%s' % (trans_uuid, root_trans_uuid)
                _is_resolved = self.resolvers.get(_resolver_id)
                _payload = TestStepPayload()
                _payload.seqID = _i
                _payload.case = 'case_%s' % self.name
                _payload.feature = self.name
                _payload.stepDesc = '%s.%s_%s.%s' % (self.name, trans.text, self.rootFeature.name, root_trans.text)
                _payload.resolved = _is_resolved is not None
                _payload.stepTotal = len(self.transitions) * len(self.rootFeature.transitions)
                _payload.fEventOnce = True
                _payload.devEventOnce = False
                _payload.fEnterEvent = _f_enter_event
                _payload.fExitEvent = _f_exit_event
                _root_src_node_uuid = root_trans.srcNodeUUID
                _root_dst_node_uuid = root_trans.dstNodeUUID
                _root_src_node = self.rootFeature.states.get(_root_src_node_uuid)
                _root_dst_node = self.rootFeature.states.get(_root_dst_node_uuid)
                _payload.devEnterEvent = _root_dst_node.enterEventModel.events if hasattr(_root_src_node,
                                                                                          'enterEventModel') else None
                _payload.devExitEvent = _root_src_node.exitEventModel.events if hasattr(_root_src_node,
                                                                                        'exitEventModel') else None
                # if transition in resolver the iter its events
                if _is_resolved is not None:
                    _payload.obos = _is_resolved
                _i += 1
                yield _payload


class TestStepPayload:
    def __init__(self):
        self.seqID = 0
        self.stepTotal = 0
        self.case = ''
        self.feature = ''
        self.stepDesc = ''
        self.resolved = False
        self.fEventOnce = False
        self.devEventOnce = False
        self.fEnterEvent = None
        self.fExitEvent = None
        self.devEnterEvent = None
        self.devExitEvent = None
        self.obos = None

    def __str__(self):
        _d = {'seqID': self.seqID,
              'stepTotal': self.stepTotal,
              'case': self.case,
              'feature': self.feature,
              'stepDesc': self.stepDesc,
              'resolved': self.resolved
              }
        return urllib.parse.urlencode(_d, doseq=True)
