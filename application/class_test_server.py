# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_test_server.py
# ------------------------------------------------------------------------------
#
# File          : class_test_server.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import threading
from xmlrpc.server import SimpleXMLRPCServer


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
