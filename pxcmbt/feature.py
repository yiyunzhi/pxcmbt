class Feature:
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._valType = str
        self._transitionOmits = dict()
        self._transitionEnters = dict()
        self._state_machine = None

    def __repr__(self):
        return 'Feature <%s>' % self._name

    @property
    def p_name(self):
        return self._name

    @property
    def p_val_type(self):
        return self._valType

    def get_state_machine(self):
        return self._state_machine

    def set_state_machine(self, machine):
        self._state_machine = machine

    def add_transition_omits(self, trans_name, parent):
        if parent not in self._transitionOmits:
            self._transitionOmits.update({parent: list()})
        self._transitionOmits[parent].append(trans_name)

    def add_transition_enters(self, trans_name, parent):
        if parent not in self._transitionEnters:
            self._transitionEnters.update({parent: list()})
        self._transitionEnters[parent].append(trans_name)

    def get_transition_omits(self):
        return self._transitionOmits

    def has_transition_omits(self, parent, name):
        if parent not in self._transitionOmits:
            return False
        return name in self._transitionOmits[parent]

    def get_transition_enters(self):
        return self._transitionEnters

    def has_transition_enters(self, parent, name):
        if parent not in self._transitionEnters:
            return False
        return name in self._transitionEnters[parent]

    def set_parent(self, parent):
        self._parent = parent

    def get_parent(self):
        return self._parent

    def has_parent(self):
        return self._parent is not None

    # def modify_up(self, other):
    #     assert isinstance(other, Feature)
    #     return [self._state_machine.get_transitions(), other.get_transition_omits()]
    #
    # def modify_down(self, other):
    #     assert isinstance(other, Feature)


class FeatureGraph:
    def __init__(self, root_feature):
        self._root = root_feature
        self._features = dict()

    def get_features(self, parent=None, recursive=False):
        if parent is None:
            parent = self._root
        if recursive:
            pass
        else:
            for k, v in self._features.items():
                if v.get_parent() is self._root:
                    yield v

    def add_feature(self, feature, parent_feature=None):
        _f_name = feature.p_name
        if _f_name not in self._features:
            if parent_feature is None:
                parent_feature = self._root
            if not feature.has_parent():
                feature.set_parent(parent_feature)
            self._features.update({_f_name: feature})

    def remove_feature(self, feature_name):
        pass

    def has_feature(self, feature_name):
        pass

    def get_root_feature(self):
        return self._root

    def set_root_feature(self, feature):
        # todo: reparent all feature
        self._root = feature


class StateMachine:
    def __init__(self, states=None, init_state=None, transition_table=None):
        self._states = states
        self._initState = init_state
        self._transitionTable = TransitionsTable(transition_table)

    def get_state(self):
        return self._states

    def get_transition_table(self):
        return self._transitionTable

    def get_current_state(self):
        pass

    def get_prev_state(self):
        pass

    def simplify(self, omitted_transitions):
        pass

    def restore(self):
        pass


class TransitionsTable:
    def __init__(self, lst_table):
        # todo: assert the format
        self._lstTable = lst_table
        self._transitions = dict()
        self._init_transitions()

    def get_transitions(self):
        _res = list()
        [_res.extend(x) for x in self._transitions.values()]
        return _res

    def get_transition_table(self):
        return self._lstTable

    def _init_transitions(self):
        for src, dst, edge in self._lstTable:
            _transition = Transition(src, dst, edge)
            if src not in self._transitions:
                self._transitions.update({src: list()})
            self._transitions[src].append(_transition)

    def remove_transition(self, src, dst):
        _tr = self.get_transition(src, dst)
        if _tr is not None:
            self._transitions[src].remove(_tr)

    def get_transition(self, src, dst):
        if src in self._transitions:
            for x in self._transitions[src]:
                if dst == x.get_destination():
                    return x
        return None


class Transition:
    def __init__(self, src, dst, edge):
        self._src = src
        self._dst = dst
        self._edge = edge

    def __repr__(self):
        return 'Transition: %s->%s' % (self._src, self._dst)

    def get_source(self):
        return self._src

    def get_destination(self):
        return self._dst

    def get_edge(self):
        return self._edge
