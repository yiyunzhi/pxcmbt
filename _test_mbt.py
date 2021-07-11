from pxcmbt.feature import Feature, FeatureGraph, StateMachine
from pxcmbt.case_generator import LivingCaseGenerator

_root_states = ['sNoPar', 'sPared', 'sRun', 'sDiag', 'sFS']
_root_tt = [
    ('sNoPar', 'sPared', 'set_parameter'),
    ('sNoPar', 'sDiag', 'set_diag'),
    ('sNoPar', 'sFS', 'set_fs'),
    ('sPared', 'sRun', 'set_run'),
    ('sPared', 'sDiag', 'set_diag'),
    ('sPared', 'sFS', 'set_fs'),
    ('sRun', 'sDiag', 'set_diag'),
    ('sRun', 'sFS', 'set_fs'),
    ('sDiag', 'sRun', 'set_acked'),
    ('sDiag', 'sFS', 'set_fs'),
    ('sFS', 'sNoPar', 'set_repower')
]
_pwr_feature_states = ['sOK', 'sUnder', 'sOver']
_pwr_feature_tt = [('sOK', 'sUnder', 'set_under'),
                   ('sOK', 'sOver', 'set_over'),
                   ('sUnder', 'sOK', 'set_ok'),
                   ('sOver', 'sOK', 'set_ok')
                   ]
_root_fsm = StateMachine(_root_states, 'sNoPar', _root_tt)
_pwr_feature_fsm = StateMachine(_pwr_feature_states, 'sOK', _pwr_feature_tt)

_root_feature = Feature('root')
_root_feature.set_state_machine(_root_fsm)
_pwr_feature = Feature('PWR')
_pwr_feature.set_state_machine(_pwr_feature_fsm)
_pwr_feature.add_transition_omits('set_fs', _root_feature)

_feature_graph = FeatureGraph(_root_feature)
_feature_graph.add_feature(_pwr_feature)
_living_case_generator = LivingCaseGenerator('TestCase AXL F PSDI 8')
_living_case_generator.set_feature_graph(_feature_graph)

if __name__ == '__main__':
    for x in _living_case_generator.generate():
        print(x.get_tested_feature(), x.get_steps(), x.get_feature_order(),x.p_steps_percent)
