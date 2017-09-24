import time
import traceback
from events import TimerEventManager, NetEventManager

from server_handler import ServerHandler


class EventServer:
    def __init__(self, conf):
        self._go = True
        self._now = None
        self._handlers = {}

        self._conf = conf

        self._net_manager = NetEventManager(conf)
        self._timer_manager = TimerEventManager(conf)

    def forever(self):
        self._listen()

        while self._go:
            self._now = int(time.time() * 1000)

            events = self._net_manager.wait()
            self._handle(events)

            events = self._timer_manager.get_expired_ev(self._now)
            self._handle(events)

    def add_handler(self, handler):
        if handler.fileno() in self._handlers:
            msg = "already has this fd <%s: %s>" \
                  % (handler.fileno(), handler)
            raise Exception(msg)

        self._handlers[handler.fileno()] = handler

    def remove_handler(self, fd):
        self._net_manager.remove(fd)
        return self._handlers.pop(fd, None)

    def get_handler(self, fd):
        return self._handlers.get(fd, None)

    def add_timer(self, timer_event):
        self._timer_manager.add(timer_event)

    def remove_timer(self, timer_event):
        self._timer_manager.remove(timer_event)

    def add_net_event(self, event):
        self._net_manager.add(event)

    def close(self):
        self._go = False

    def _listen(self):
        addresses = set()

        for svr, conf in self._conf["servers"].iteritems():
            addresses.add(conf['listen'])

        for addr in addresses:
            handler = ServerHandler(addr, self, self._conf)
            self.add_handler(handler)

    def _handle(self, event_list):
        try:
            for ev in event_list:
                handler = self._handlers[ev.fd]
                handler.handle(ev)
        except:
            traceback.print_exc()
