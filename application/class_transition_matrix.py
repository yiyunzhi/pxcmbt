import itertools
import numpy as np


class TransitionNode:
    def __init__(self, transition):
        self.transition = transition
        self.isReadonly = False
        self.isEnable = True

    def __repr__(self):
        return 'TransitionNode: %s' % self.transition


class TransitionMatrix:
    """
    used for storing the matrix data of the result, which dotted transitions from two
    statemachines.
    """

    def __init__(self, state_model_a, state_model_b):
        self.aModel = state_model_a
        self.bModel = state_model_b
        self.aTrans = state_model_a.get_transitions()
        self.bTrans = state_model_b.get_transitions()
        self.matrix = list()
        for x in self.aTrans:
            self.matrix.append((TransitionNode(x), [TransitionNode(y) for y in self.bTrans]))
