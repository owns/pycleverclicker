#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-26
<desc here>
"""

import time
from threading import Thread, Lock
from pynput import mouse, keyboard

from packages.pymybase.myloggingbase import MyLoggingBase

class MyPlayer(Thread,MyLoggingBase):
    """play recording mouse and keyboard inputs"""
    
    PRECISION = 4
    __continue_running = True
    __queue = None
    __root = None
    __time_lock = None
    __key_lock = None
    __pressed_keys = None
    __last_time = None
    log_clicks = True
    log_keys = True

    def __init__(self,root, actions_queue,*args,**keys):
        MyLoggingBase.__init__(self,*args,**keys)
        Thread.__init__(self,*args,**keys)

        self.__root = root
        self.__queue = actions_queue
        self.__time_lock = Lock()
        self.__key_lock = Lock()
    
    #===========================================================================
    # STOP
    #===========================================================================
    def stop(self):
        """ start stopping ..."""
        self.logger.info('told to stop ...')
        self.__continue_running = False

    #===========================================================================
    # RUN
    #===========================================================================
    def run(self):
        """ do work here """
        self.logger.info('started')
        self.__pressed_keys = dict()
        self.__last_time = None

        #=======================================================================
        # # start listeners
        #=======================================================================
        '''
        list_m = mouse.Listener(on_click=self.on_click)
        list_m.start()
        list_m.wait()
        list_k = keyboard.Listener(on_release=self.on_release,
                                   on_press=self.on_press)
        list_k.start()
        list_k.wait()

        #=======================================================================
        # wait to stop
        #=======================================================================
        while self.__continue_running: time.sleep(.5)

        #=======================================================================
        # stop listeners
        #=======================================================================
        # NOTE: ubuntu will wait for input before really stopping ...
        list_m.stop()
        mouse.Controller().move(1,1) # ubuntu will wait for input before really stopping ...
        self.logger.debug('joining mouse listener...')
        list_m.join()
        list_k.stop()
        k = keyboard.Controller() # ubuntu will wait for input before really stopping ...
        k.press(keyboard.Key.shift)
        k.release(keyboard.Key.shift)
        self.logger.debug('joining keyboard listener...')
        list_k.join()
        '''
        self.logger.info('stopped')





