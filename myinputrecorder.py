#!/usr/bin/env python3
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-26
<desc here>
"""

import time
from pynput import mouse
from pynput import keyboard

from pymybase.myloggingbase import MyLoggingBase
from threading import Thread
from threading import Lock

class MyInputRecorder(Thread,MyLoggingBase):

    __continue_running = True
    __queue = None
    __time_lock = None
    __last_time = None
    
    IGNORE_KEYS = (keyboard.Key.shift,keyboard.Key.shift_l,keyboard.Key.shift_r,
                   keyboard.Key.ctrl,keyboard.Key.ctrl_l,keyboard.Key.ctrl_r,
                   keyboard.Key.alt,keyboard.Key.alt_gr,keyboard.Key.alt_l,keyboard.Key.alt_r,
                   keyboard.Key.cmd,keyboard.Key.cmd_l,keyboard.Key.cmd_r)
    
    def __init__(self,actions_queue,*args,**keys):
        MyLoggingBase.__init__(self,*args,**keys)
        Thread.__init__(self,*args,**keys)
        
        self.__queue = actions_queue
    
    #===========================================================================
    # on_click
    #===========================================================================
    def on_click(self,x,y,button,pressed):
        if not pressed:
            with self.__time_lock:
                t = time.time()
                if not self.__last_time: self.__last_time = t
                self.__queue.put_nowait(dict(type='mouse',name=button.name,pos=(x,y),time=t-self.__last_time))
                #self.__queue.put_nowait('{0!s} click at {1!s}'.format(button.name,(x,y)))
                self.__last_time = t
    
    #===========================================================================
    # on_release
    #===========================================================================
    def on_release(self,key):
        if key not in keyboard.Key:
            k = key.char
            if not k.isalnum(): # or k != k.lower():
                self.logger.warn('invalid key %r',key)
                return None # stop
        
        with self.__time_lock:
            t = time.time()
            if not self.__last_time: self.__last_time = t
            try: self.__queue.put_nowait(dict(type='type',name=key.char,time=t-self.__last_time))
            except AttributeError:
                if key not in self.IGNORE_KEYS:
                    self.__queue.put_nowait(dict(type='type',name=key.name,time=t-self.__last_time))
                    self.__last_time = t
            else: self.__last_time = t
    
    #===========================================================================
    # STOP
    #===========================================================================
    def stop(self):
        """ start stopping ..."""
        self.logger.debug('told to stop')
        self.__continue_running = False
        
    #===========================================================================
    # RUN
    #===========================================================================
    def run(self):
        """ do work here """
        self.logger.debug('start')
        self.__time_lock = Lock()
        self.__last_time = None
        
        #=======================================================================
        # # start listeners
        #=======================================================================
        list_m = mouse.Listener(on_click=self.on_click)
        list_m.start()
        list_m.wait()
        list_k = keyboard.Listener(on_release=self.on_release)
        list_k.start()
        list_k.wait()
        
        #=======================================================================
        # wait to stop
        #=======================================================================
        while self.__continue_running: time.sleep(.5)
        
        #=======================================================================
        # stop listeners
        #=======================================================================
        list_m.stop()
        list_k.stop()
        self.logger.debug('joining mouse listener...')
        list_m.join()
        self.logger.debug('joining keyboard listener...')
        list_k.join()
            
        self.logger.debug('stop')
        
        
        
        
        
        
        
        