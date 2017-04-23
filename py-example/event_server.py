import signal
from select import epoll, EPOLLET, EPOLLIN, EPOLLOUT, EPOLLHUP


class Event:
    def __init__(self, handler=None):
        self.sig = False

        self.timer = False

        self.et = False
        self.hup = False
        self.read = False
        self.write = False

        self.handler = handler

    def set_epoll_event(self, event_mask):
        if event_mask | EPOLLHUP:
            self.hup = True

        if event_mask | EPOLLOUT:
            self.write = True

        if event_mask | EPOLLIN:
            self.read = True

    def get_epoll_event(self):
        event_mask = 0

        if self.read:
            event_mask |= EPOLLIN

        if self.write:
            event_mask |= EPOLLOUT

        if self.hup:
            event_mask |= EPOLLHUP

        if self.et:
            event_mask |= EPOLLET

        return event_mask

    def __str__(self):
        str_format = 'Event: sig = %s, timer= %s, et = %s, hup = %s, read= %s, write= %s, handler = %s'
        return str_format % (self.sig, self.timer, self.et, self.hup, self.read, self.write, self.handler)


class EventServer:
    def __init__(self, max_wait_time):
        self._max_wait_time = max_wait_time

        self._epoll_handler_dict = {}
        self._timer_handler_dict = {}
        self._signal_handler_dict = {}

        self._epoll = epoll()

    def add_handler(self, event):
        if event.sig:
            sig = event.handler.id()
            if sig in self._signal_handler_dict:
                raise Exception('already handled sig %s' % sig)
            self._signal_handler_dict[sig] = event.handler
            signal.signal(sig, self._event_on_signal)
            return

        if event.timer:
            # TODO
            self._signal_handler_dict[event.handler.id()] = event.handler
            return

        self._epoll_handler_dict[event.handler.id()] = event.handler
        self._epoll.register(event.handler.id(), event.get_epoll_event())

    def remove_handler(self, event):
        if event.sig:
            raise Exception('can not remove signal handlers')
            return

        if event.timer:
            # TODO
            del self._signal_handler_dict[event.handler.id()]
            return

        del self._epoll_handler_dict[event.handler.id()]
        self._epoll.unregister(event.handler.id())

    def poll(self):
        event_list = []

        for fd, ev in self._epoll.poll(timeout=self._max_wait_time):
            event = Event(self._epoll_handler_dict[fd])
            event.set_epoll_event(ev)
            event_list.append(event)

        # TODO find expired timers

        return event_list

    def _event_on_signal(self, sig, _):
        if sig not in self._signal_handler_dict:
            return

        event = Event()
        event.sig = True
        self._signal_handler_dict[sig].handle(event)
