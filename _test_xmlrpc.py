import datetime, threading
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from collections import OrderedDict
from application.class_transition_matrix import TransitionMatrix
from application.class_state_model import StateModel
from transitions import Machine, Transition

# assume get we follow data from canvas
fa_states = ['faA', 'faB', 'faC']
fa_state_event = {'faA': [('EvtEnterA', 'EvtEnterA2')]}
fa_states_init = 'faA'
fa_transitions = [
    {'trigger': 't0fa', 'source': 'faA', 'dest': 'faB', 'after': 'emit_transition_event', 'name': 't0fa',
     'evts': ['EvtfaAB'], 'uuid': 'fadwafw'},
    {'trigger': 't1fa', 'source': 'faB', 'dest': 'faC', 'after': 'emit_transition_event', 'name': 't1fa',
     'evts': ['EvtfaBC'], 'uuid': 'fadwafw'}
]

fb_states = ['fbA', 'fbB', 'fbC']
fb_state_event = {'fbA': [('EvtEnterA', 'EvtEnterA2')]}
fb_states_init = 'fbA'
fb_transitions = [
    {'trigger': 't0fb', 'source': 'fbA', 'dest': 'fbB', 'after': 'emit_transition_event', 'name': 't0fb',
     'evts': ['EvtfbAB'], 'uuid': 'fbdwafw'},
    {'trigger': 't1fb', 'source': 'fbB', 'dest': 'fbC', 'after': 'emit_transition_event', 'name': 't1fb',
     'evts': ['EvtfbBC'], 'uuid': 'fbdwafw'}
]

fc_states = ['fcA', 'fcB', 'fcC']
fc_state_event = {'fcA': [('EvtEnterA', 'EvtEnterA2')]}
fc_states_init = 'fcA'
fc_transitions = [
    {'trigger': 't0fc', 'source': 'fcA', 'dest': 'fcB', 'after': 'emit_transition_event', 'name': 't0fc',
     'evts': ['EvtfcAB'], 'uuid': 'fcdwafw'},
    {'trigger': 't1fc', 'source': 'fcB', 'dest': 'fcC', 'after': 'emit_transition_event', 'name': 't1fc',
     'evts': ['EvtfcBC'], 'uuid': 'fcdwafw'}
]

fd_states = ['fdA', 'fdB', 'fdC']
fd_state_event = {'fdA': [('EvtEnterA', 'EvtEnterA2')]}
fd_states_init = 'fdA'
fd_transitions = [
    {'trigger': 't0fd', 'source': 'fdA', 'dest': 'fdB', 'after': 'emit_transition_event', 'name': 't0fd',
     'evts': ['EvtfdAB'], 'uuid': 'fddwafw'},
    {'trigger': 't1fd', 'source': 'fdB', 'dest': 'fdC', 'after': 'emit_transition_event', 'name': 't1fd',
     'evts': ['EvtfdBC'], 'uuid': 'fddwafw'}
]

froot_states = ['frootA', 'frootB', 'frootC']
froot_state_event = {'frootA': [('EvtEnterA', 'EvtEnterA2')]}
froot_states_init = 'frootA'
froot_transitions = [
    {'trigger': 't0froot', 'source': 'frootA', 'dest': 'frootB', 'after': 'emit_transition_event', 'name': 't0froot',
     'evts': ['EvtfrootAB'], 'uuid': 'frootdwafw'},
    {'trigger': 't1froot', 'source': 'frootB', 'dest': 'frootC', 'after': 'emit_transition_event', 'name': 't1froot',
     'evts': ['EvtfrootBC'], 'uuid': 'frootdwafw'}
]


class Feature:
    def __init__(self, uuid, name, state_model, events=None):
        self.uuid = uuid
        self.name = name
        self.stateModel = state_model
        self.events = events
        self.transMatrix = None

    def __ilshift__(self, other):
        assert isinstance(other, Feature)
        if self.stateModel is not None and other.stateModel is not None:
            self.transMatrix = TransitionMatrix(self.stateModel, other.stateModel)
        return self


statemodel_a = StateModel(fa_states, fa_states_init, fa_transitions)
statemodel_b = StateModel(fb_states, fb_states_init, fb_transitions)
statemodel_c = StateModel(fc_states, fc_states_init, fc_transitions)
statemodel_d = StateModel(fd_states, fd_states_init, fd_transitions)
statemodel_root = StateModel(froot_states, froot_states_init, froot_transitions)

feature_a = Feature('a', 'A', statemodel_a)
feature_b = Feature('b', 'B', statemodel_b)
feature_c = Feature('c', 'C', statemodel_c)
feature_d = Feature('d', 'D', statemodel_d)
feature_root = Feature('root', 'Root', statemodel_root)
feature_a <<= feature_root
feature_b <<= feature_root
feature_c <<= feature_root
feature_d <<= feature_root


class MBTRunner:
    def __init__(self, features=None):
        self.features = OrderedDict()
        if features is not None and isinstance(features, list):
            [self.features.update({x.uuid: x}) for x in features]

    def add_feature(self, feature):
        self.features.update({feature.uuid: feature})

    def remove_feature(self, uuid):
        if uuid in self.features:
            self.features.pop(uuid)

    def build(self):
        # todo: suite=A&case=a_pwr&step=0&feature=a&levent=dd0&revent=ortrr&callback=stepdone
        for uid, feature in self.features.items():
            _trans_matrix = feature.transMatrix
            _lst_trans_ma = _trans_matrix.matrix
            for a, b in _lst_trans_ma:
                _left_feature_evts = a.transition.events
                #getattr(feature.stateModel, a.transition.name)(_left_feature_evts)
                for bb in b:
                    _right_feature_evts = bb.transition.events
                    #getattr(_trans_matrix.bModel, bb.transition.name)(_right_feature_evts)
                    yield feature.name, _left_feature_evts, _right_feature_evts

    def next(self):
        return next(self._get())

    def abort(self):
        pass


class MBTOnlineTestServer:
    def __init__(self, runner):
        self.port = 8180
        self.address = 'localhost'
        self.isRunning = False
        self.runner = runner
        self.rpcServerThread = threading.Thread(target=self._run)
        self.rpcServer = None

    def _run(self):
        print("MBTTestServer Listening on port 8180...")
        self.rpcServer = SimpleXMLRPCServer(("localhost", 8180))
        self.rpcServer.register_instance(self.runner, True)
        self.rpcServer.serve_forever()

    def start(self):
        if not self.isRunning:
            self.rpcServerThread.start()
            self.isRunning = True

    def stop(self):
        if self.isRunning:
            if self.rpcServer is not None:
                self.rpcServer.shutdown()
            self.isRunning = False


_mbt_test_runner = MBTRunner()
_mbt_test_runner.add_feature(feature_a)
_mbt_test_runner.add_feature(feature_b)
_mbt_test_runner.add_feature(feature_c)
_mbt_test_runner.add_feature(feature_d)

# _mbt_test_server = MBTOnlineTestServer(_mbt_test_runner)
# _mbt_test_server.start()
# print('TestServer started')
_cases=_mbt_test_runner._get()
print(next(_cases))
print(next(_cases))
print(next(_cases))
print(next(_cases))