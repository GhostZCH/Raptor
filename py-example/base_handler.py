
class BaseHandler:
    def __init__(self, handler_id, event_server):
        self._id = handler_id
        self._svr = event_server

    def id(self):
        return self._id

    def handle(self, event):
        raise NotImplementedError('BaseHandler')
