# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_transition_matrix.py
# ------------------------------------------------------------------------------
#
# File          : class_transition_matrix.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import numpy as np


class TransitionMatrixNode:
    def __init__(self, row_trans, col_trans):
        self.rowTrans = row_trans
        self.colTrans = col_trans
        self.isChecked = False
        self.isReadonly = False
        self.isEnabled = True


class TransitionMatrix:
    def __init__(self, state_machine):
        # todo: use numpy store the data
        self.nodes = None

    def get_size(self):
        pass

    def get_enabled_count(self):
        pass

    def left_join(self, state_machine):
        pass

    def right_join(self, state_machine):
        pass
