import signal
from event_server import Event, EventServer

from host_handler import HostHandler
from signal_handler import SignalHandler


class Worker:
    def __init__(self, worker_id, conf, host):
        self._id = worker_id
        self._conf = conf
        self._host = host
        self._event_server = None
        self._go = True

    def stop(self):
        print 'worker %d stop on sig' % self._id
        self._go = False

    def start(self):
        self._event_server = EventServer(1)

        sigint_event = Event(SignalHandler(signal.SIGINT, self.stop, self._event_server))
        sigint_event.sig = True
        self._event_server.add_handler(sigint_event)

        host_event = Event(HostHandler(self._host, self._conf, self._event_server))
        host_event.read = True
        host_event.write = True
        host_event.et = False
        host_event.hup = True
        self._event_server.add_handler(host_event)

        while self._go:
            print 'worker', self._id, 'run'
            for event in self._event_server.poll():
                event.handler.handle(event)

        print 'worker %d exit' % self._id
