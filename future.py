"""This module tries to mimics the behaviour of Future module
This represents the object whose value has not been returned yet"""

'''Define a class with some basic public interface

#future can have its current state pending; or finished;'''
import threading
class ResultNotSetError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(value)

class Future:

    _PENDING = 'pending'
    _FINISHED = 'finished'

    def __init__(self):
        
        self._done_callbacks = [] #list of callback to be called when result is set
        self._result = None
        self._state = self._PENDING
        self._exception = None
        self._mutex = threading.Lock()
        self._done = False
        
    
    
    def set_result(self, result):
        if self._done:
            raise ValueError('Result can only be set once')
        
        #set the result and call the callbacks passing the future instance to each one of them
        self._result = result
        self._done = True
        self._state = self._FINISHED
        #now finally call the callbacks
        for cb in self._done_callbacks:
            cb(self)
        
    def set_exception(self, excp):
        if self._done:
            raise ValueError('Result/Exception can only be set once')
        self._exception = excp
        self._done = True
        self._state = self._FINISHED

    
    def result(self):
        if not self._done:
            raise ResultNotSetError('Result not set')
        
        return self._result or self._exception
        

    def add_done_callback(self, cb):
        self._done_callbacks.append(cb)

    
    def done(self):
        return self._done

    def __repr__(self):
        return '<Future State : %s Result : %s>' % (self._state, str(self._result))
    
    
        