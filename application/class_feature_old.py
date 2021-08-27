# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_feature.py
# ------------------------------------------------------------------------------
#
# File          : class_feature.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import urllib.parse
from .class_transition_matrix import TransitionMatrix


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
