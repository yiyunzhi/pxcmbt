import functools, operator, math
from itertools import product


class CaseGenerator:
    def __init__(self, case_name):
        self._name = case_name
        self._featureGraph = None

    def get_feature_graph(self):
        return self._featureGraph

    def set_feature_graph(self, feature_graph):
        self._featureGraph = feature_graph

    def generate(self, mode=0):
        raise NotImplemented()


# todo: generate LivingCase
class LivingCaseGenerator(CaseGenerator):
    def __init__(self, name):
        super(LivingCaseGenerator, self).__init__('Living_%s' % name)

    def generate(self, mode=0):
        if mode == 0:
            _features = self._featureGraph.get_features()
            # feature will be generate one each after another
            for f in _features:
                _parent = f.get_parent()
                _used_transition = list()
                _features_order = [f]
                _f_transitions = f.get_state_machine().get_transition_table().get_transitions()
                _used_transition.append(_f_transitions)
                # fetch all parent transitions, because is mode 0
                while _parent:
                    _parent_transitions = _parent.get_state_machine().get_transition_table().get_transitions()
                    _used_transition.append(_parent_transitions)
                    _features_order.append(_parent)
                    _parent = _parent.get_parent()
                _count = functools.reduce(operator.mul, map(len, _used_transition), 1)
                _product_result = product(*_used_transition)
                for x in _product_result:
                    yield TestStepContext(f, _features_order, x, _count)


class ScriptCaseGenerator(CaseGenerator):
    def __init__(self, name):
        super(ScriptCaseGenerator, self).__init__('Living_%s' % name)


class TestStepContext:
    # todo: instance as a contextManager, implements __enter__, __exit__
    def __init__(self, tested_feature, feature_order, test_steps, whole_count):
        self._testedFeature = tested_feature
        self._featureOrder = feature_order
        self._steps = test_steps
        self._wholeCount = whole_count

    def __repr__(self):
        _s = '%s|%s\n' % (self._steps, '')
        return _s

    @property
    def p_steps_percent(self):
        # todo: after wash should be this attr recalculated
        return round(len(self._steps) / self._wholeCount, 4)

    def get_steps(self):
        return self._steps

    def get_tested_feature(self):
        return self._testedFeature

    def get_feature_order(self):
        return self._featureOrder
