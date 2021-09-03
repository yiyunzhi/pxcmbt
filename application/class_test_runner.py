# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_test_runner.py
# ------------------------------------------------------------------------------
#
# File          : class_test_runner.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from collections import OrderedDict
from pubsub import pub
from application.define import EnumTCStatus, EnumAppSignals


class MBTRunner:
    def __init__(self, features=None):
        self.features = OrderedDict()
        self.cases = list()
        if features is not None and isinstance(features, list):
            [self.features.update({x.uuid: x}) for x in features]
            self.build()
        self.cursor = 0

    def add_feature(self, feature):
        self.features.update({feature.uuid: feature})

    def remove_feature(self, uuid):
        if uuid in self.features:
            self.features.pop(uuid)

    def build(self):
        self.cases.clear()
        for uid, feature in self.features.items():
            [self.cases.append(x) for x in feature]

    def next(self):
        if self.cursor + 1 == len(self.cases):
            return '__END__'
        _case = self.cases[self.cursor]
        pub.sendMessage(EnumAppSignals.sigV2VCurrentTCChanged.value, index=self.cursor)
        self.cursor += 1
        return _case

    def set_state(self, state):
        pub.sendMessage(EnumAppSignals.sigV2VCurrentTCStatusChanged.value, status=state)

    def reset(self):
        self.cursor = 0
