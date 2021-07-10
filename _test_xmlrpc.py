import datetime, threading
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from collections import OrderedDict
from application.class_transition_matrix import TransitionMatrix
from application.class_state_model import StateModel
from transitions import Machine, Transition
import urllib.parse

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
        self.bFeature = None

    def __ilshift__(self, other):
        assert isinstance(other, Feature)
        self.bFeature = other
        if self.stateModel is not None and other.stateModel is not None:
            self.transMatrix = TransitionMatrix(self.stateModel, other.stateModel)
        return self

    @property
    def p_suite_name(self):
        if self.bFeature is None:
            return None
        return '%s_%s' % (self.name, self.bFeature.name)

    @property
    def p_cases(self):
        if self.bFeature is None or self.transMatrix is None:
            return None
        _cases = list()
        for x in self.stateModel.states:
            pass
        return _cases

    def __iter__(self):
        if self.transMatrix is not None:
            _lst_trans_ma = self.transMatrix.matrix
            # suite=a_pwr&case=a_sok&step=0&feature=a&levent=dd0&leventdata=00&revent=ortrr&reventdata=12&callback=stepdone
            for a, b in _lst_trans_ma:
                _left_feature_evts = a.transition.events
                _step = 0
                for bb in b:
                    _step += 1
                    _right_feature_evts = bb.transition.events
                    # todo: add leventData,reventdata
                    _params = {'suite': self.p_suite_name,
                               'case': '%s_%s' % (a.transition.name, bb.transition.name),
                               'step': _step,
                               'stepTotal': len(b),
                               'feature': self.name,
                               'levent': _left_feature_evts,
                               'revent': _right_feature_evts,
                               'callback': 'stepdone'
                               }
                    yield urllib.parse.urlencode(_params, doseq=True)
        else:
            return None


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
            self.build()
        self.suites = list()
        self.cursor = 0

    def add_feature(self, feature):
        self.features.update({feature.uuid: feature})

    def remove_feature(self, uuid):
        if uuid in self.features:
            self.features.pop(uuid)

    def build(self):
        self.suites.clear()
        for uid, feature in self.features.items():
            [self.suites.append(x) for x in feature]

    def next(self):
        _params = {'cursor': self.cursor,
                   'total': len(self.suites),
                   }
        _progress_info = urllib.parse.urlencode(_params, doseq=True)
        if self.cursor >= len(self.suites):
            _state_info = 'state=END'
            _res = '%s&%s' % (_state_info, _progress_info)
        else:
            _state_info = 'state=OK'
            _res = self.suites[self.cursor]
            self.cursor += 1
            _res = '%s&%s&%s' % (_state_info, _res, _progress_info)
        return _res

    def get_percent(self):
        if self.suites:
            return self.cursor / len(self.suites)
        else:
            return .0

    def abort(self):
        return True

    def restart(self):
        self.build()
        self.cursor = 0
        return True

    def restart_from(self, cursor):
        if cursor < len(self.suites):
            self.cursor = cursor
            return True
        else:
            return False


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
_mbt_test_runner.build()
# _mbt_test_server = MBTOnlineTestServer(_mbt_test_runner)
# _mbt_test_server.start()
# print('TestServer started')
for i in range(20):
    print('-->', _mbt_test_runner.next())
_mbt_test_runner.restart()
print('---->restart<-------')
for i in range(20):
    print('-->', _mbt_test_runner.next())
