from base_handler import BaseHandler


class SignalHandler(BaseHandler):
    def __init__(self, sig, event_server, call_back):
        BaseHandler.__init__(self, sig, event_server)
        self._call_back = call_back

    def handle(self, event):
        if not event.sig:
            raise Exception(str(event))

        self._call_back()
