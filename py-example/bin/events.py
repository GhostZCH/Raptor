from select import epoll, EPOLLET, EPOLLHUP, EPOLLIN, EPOLLOUT


class EventBase:
    def __init__(self, fd):
        self.fd = fd


class NetEvent(EventBase):
    def __init__(self, fd, epoll_event=0):
        EventBase.__init__(self, fd)

        self.read = epoll_event & EPOLLIN
        self.write = epoll_event & EPOLLOUT
        self.error = epoll_event & EPOLLHUP
        self.et = epoll_event & EPOLLET

    def get_mask(self):
        mask = 0

        if self.read:
            mask |= EPOLLIN

        if self.write:
            mask |= EPOLLOUT

        if self.error:
            mask |= EPOLLHUP

        if self.et:
            mask |= EPOLLET

        return mask


class TimerEvent(EventBase):
    def __init__(self, fd, expired_ms, event_id):
        EventBase.__init__(self, fd)
        self.expired_ms = expired_ms
        self.event_id = event_id

        self._hash = hash((self.fd, self.expired_ms, self.event_id))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (self.fd, self.expired_ms, self.event_id)\
               == (other.fd, other.expired_ms, other.event_id)


class TimerEventManager:
    _TIME_SPAN = 1000

    def __init__(self, conf):
        self._conf = conf
        self._timers = {}  # like map in c++

    def get_expired_ev(self, now_ms):
        expired_events = set()

        time_key = self._get_key(now_ms)

        last_time_key = time_key - 1
        if last_time_key in self._timers:
            for events in self._timers[last_time_key].values():
                expired_events.update(events)
            self._timers.pop(last_time_key)

        if time_key in self._timers:
            for expired_ms in self._timers[time_key].keys():
                if expired_ms < now_ms:
                    events = self._timers[time_key].pop(expired_ms)
                    expired_events.update(events)

        return expired_events

    def add(self, timer_event):
        expired_ms = timer_event.expired_ms
        key = self._get_key(expired_ms)

        self._timers.setdefault(key, {})
        self._timers[key].setdefault(expired_ms, set())
        self._timers[key][expired_ms].add(timer_event)

    def remove(self, timer_event):
        expired_ms = timer_event.expired_ms
        key = self._get_key(expired_ms)

        if key not in self._timers:
            return

        if expired_ms not in self._timers[key]:
            return

        self._timers[key][expired_ms].remove(timer_event)

    def _get_key(self, time_ms):
        return time_ms / self._TIME_SPAN


class NetEventManager:
    def __init__(self, conf):
        self._conf = conf
        self._epoll = epoll()

    def add(self, event):
        self._epoll.register(event.fd, event.get_mask())

    def remove(self, fd):
        self._epoll.unregister(fd)

    def wait(self):
        ev_list = self._epoll.poll()
        ev_list = [NetEvent(fd, epoll_event=ev) for fd, ev in ev_list]
        return ev_list
