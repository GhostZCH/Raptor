import signal
import os
from event_server import Event, EventServer
from signal_handler import SignalHandler


class Master:
    def __init__(self, host, conf):
        self._conf = conf
        self._host = host
        self._go = True
        self._child_list = []
        self._event_server = None

    def start(self):
        self._event_server = EventServer(1)

        sigint_event = Event(SignalHandler(signal.SIGINT, self._event_server, self.stop))
        sigint_event.sig = True
        self._event_server.add_handler(sigint_event)

        sigchld_event = Event(SignalHandler(signal.SIGCHLD, self._event_server, self.stop))
        sigchld_event.sig = True
        self._event_server.add_handler(sigchld_event)

        while self._go:
            self._event_server.poll()
            print 'master run', self._child_list

        print 'master stop'

        for cld in self._child_list:
            os.kill(cld, signal.SIGINT)

        self._host.cloes()

    def add_child(self, pid):
        self._child_list.append(pid)

    def stop(self):
        # print 'maser stop'
        self._go = False

import time
time.time()


