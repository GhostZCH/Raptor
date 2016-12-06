import time


class Master:
    def __init__(self, conf):
        self._conf = conf

    def start(self):
        while True:
            time.sleep(1)
            print 'master'
