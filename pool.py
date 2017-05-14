"""This module mimics the behaviour of threadpool"""

import os
import threading
import queue

from concurrent.futures import Future


class Work:
    """This class represents the unit of work"""

    def __init__(self, fut, fn, args, kwargs):
        self.fut = fut
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.fut.set_exception(e)
        else:
            self.fut.set_result(result)


def _worker(pool_ref, work_queue):

    def get_or_None():
        nonlocal work_queue
        try:
            work_item = work_queue.get(block=False)
        except queue.Empty:
            return None
        else:
            return work_item

    try:
        while True:
            if pool_ref._shutdown:
                break
            
            work_item = get_or_None()
            if work_item is None:
                continue
            work_item.run()
                
            
            #if work_item is None, it means we need to close the worker
            
        
    except BaseException as e:
        #for this use the logging module
        print(e)
    finally:
        return

class ThreadPool:
    
    def __init__(self, max_workers=None):
        if max_workers is None:
            max_workers = (os.cpu_count() or 1) * 5
        if max_workers <= 0:
            raise ValueError('workers cannot be less than 1')
        
        self._max_workers = max_workers
        self._work_queues = queue.Queue()
        self._threads = set()
        self._shutdown = False
        self._mutex = threading.Lock()

        
    @property
    def _full(self):
        return False if len(self._threads) < self._max_workers else True

    def submit(self, fn, *args, **kwargs):
        #craete a work unit
        _future = Future()
        _work = Work(_future, fn, args, kwargs)
        #good techinique
        self._full or self._handle_threads()
        with self._mutex: #make it thread safe
            self._work_queues.put(_work)
        return _future

        
    def shutdown(self):
        self._shutdown = True
        #self._work_queues.put(None)
    
    def _handle_threads(self):
        #new thread
        t = threading.Thread(target=_worker, args=(self, self._work_queues,))
        t.setDaemon(True)
        t.start()

        self._threads.add(t)

