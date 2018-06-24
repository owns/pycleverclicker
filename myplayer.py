#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-26
<desc here>
"""

import time
import random
from threading import Thread, Event
from pynput import mouse, keyboard

from packages.pymybase.myloggingbase import MyLoggingBase

class MyPlayer(Thread,MyLoggingBase):
    """play recording mouse and keyboard inputs"""
    
    PRECISION = 4
    __evt = None
    __root = None
    __queue = None
    __actions = None
    __settings = None

    def __init__(self,root, actions_queue, actions, settings, *args,**keys):
        MyLoggingBase.__init__(self,*args,**keys)
        Thread.__init__(self,*args,**keys)

        self.__root = root
        self.__evt = Event()
        self.__queue = actions_queue
        self.__actions = actions
        self.__settings = settings
    
    #===========================================================================
    # STOP
    #===========================================================================
    def stop(self):
        """ start stopping ..."""
        self.__evt.set()
        self.logger.info('told to stop ...')

    #===========================================================================
    # RUN
    #===========================================================================
    def run(self):
        """ do work here """
        self.logger.info('started')
        
        #=======================================================================
        # start controllers
        #=======================================================================
        m = mouse.Controller()
        k = keyboard.Controller()
        self.logger.debug('keyboard and mouse controller set')
        
        #=======================================================================
        # do automation
        #=======================================================================
        # wait delay
        repeat =  self.__settings['repeat limit']
        start_delay = self.__settings['start delay']
        start_var = self.__settings['start variance']
        action_var = self.__settings['action variance']
        
        # keep going
        run_count = 1
        while not self.__evt.is_set():
            # start delay?
            t = start_delay + random.uniform(-start_var, start_var)
            if t > 0:
                self.logger.info('%03d sleeping start delay, %.3f', run_count, t)
                if self.__evt.wait(t): break
            else:
                self.logger.info('%03d sleeping start delay, %.3f', 
                                 run_count, start_delay)
            
            # go though each action
            for action in self.__actions:
                t = action['time'] + random.uniform(-action_var, action_var)
                
                # wait if needed
                if t > 0:
                    if self.__evt.wait(t): break
                
                # do action
                if action['type'] == 'keyboard':
                    self.logger.info('%.3f %s released after %.1f',
                                     action['time'],action['name'],action['pressed'])
                elif action['type'] == 'mouse':
                    self.logger.info('%.3f %s click at %s',
                                     action['time'],action['name'],action['pos'])
                else:
                    self.logger.error('unable to perform action type "%s"',action['type'])
            
            # continue?
            if run_count == repeat: break
            run_count += 1
        
        '''
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





