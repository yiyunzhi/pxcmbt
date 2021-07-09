from transitions import Machine, Transition
from .class_transition_matrix import TransitionMatrix


class MBTEvtTransition(Transition):
    def __init__(self, *args, **kwargs):
        self.events = kwargs.pop('evts') if 'evts' in kwargs else None
        self.name = kwargs.pop('name') if 'name' in kwargs else None
        self.uuid = kwargs.pop('uuid') if 'uuid' in kwargs else None
        Transition.__init__(self, *args, **kwargs)


class StateModel(Machine):
    """
    used as model of transitions.Machine
    StateModel().state_name() could be called and emit a event
    """
    transition_cls = MBTEvtTransition

    def __init__(self, states, init_state, transitions=None):
        Machine.__init__(self, states=states, initial=init_state, transitions=transitions, auto_transitions=False)

    def emit_transition_event(self, *args, **kwargs):
        print('emit_transition_event', args, kwargs)
