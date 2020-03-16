import sys
import threading
import psutil
import os
from Infrastructure import log
process = psutil.Process(os.getpid())


logger = log.get_logger("THREAD_RUNNER")


class Runner:

    def __init__(self):
        self.logger = logger

    def set_interval(self, func, sec, name, descriptor):
        # each interval run in a different thread
        def func_wrapper():
            func(descriptor, sec, t1)
            self.set_interval(func, sec, name, descriptor)
            t1.kill()
            if not t1.is_alive():
                self.logger.info("Thread killed {}")

        t1 = ThreadWithTrace(target=func_wrapper)
        t1.start()
        return t1


class ThreadWithTrace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        threading.Thread.start(self)

    def kill(self):
        self.killed = True
