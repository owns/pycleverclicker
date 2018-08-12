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
    UPDATE_EVERY = 1
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
        msg_prefix = '{0:03}/{1:03}' if repeat else '{0:03}'
        
        run_count = 1
        while not self.__evt.is_set():
            # start delay?
            t = start_delay + random.uniform(-start_var, start_var)
            if t > 0:
                self.logger.debug('%03d sleeping start delay, %.3f', run_count, t)
                # add to queue so app can log to console
                self.__queue.put_nowait(dict(
                    run = msg_prefix.format(run_count,run_count),
                    msg = ' starting in {0:02} ...',
                    time = time.time() + t))
                if self.__evt.wait(t): break
            else:
                self.logger.info('%03d sleeping start delay, %.3f', 
                                 run_count, start_delay)
            
            # told to stop?
            if self.__evt.is_set(): break
            
            # go though each action
            for action in self.__actions:
                t = action['time'] + random.uniform(-action_var, action_var)
                
                # add to queue so app can log to console
                self.__queue.put_nowait(dict(
                    run = msg_prefix.format(run_count,run_count),
                    msg = '"'+action['name']+'" in {0:02} ...',
                    time = time.time() + t))
                
                # wait if needed
                if t > 0 and self.__evt.wait(t): break
                
                # do action
                action_name = action['name']
                if action['type'] == 'keyboard':
                    t = action['pressed']
                    self.logger.debug('%.3f %s released after %.1f',
                                     action['time'],action_name,t)
                    k.press(action_name if len(action_name)==1 else keyboard.Key[action_name]) # press
                    if t > 0 and self.__evt.wait(t): break # hold press
                    k.release(action_name if len(action_name)==1 else keyboard.Key[action_name]) # release
                    
                elif action['type'] == 'mouse':
                    self.logger.debug('%.3f %s click at %s',
                                     action['time'],action_name,action['pos'])
                    m.position = action['pos'] # move
                    m.click(mouse.Button[action_name]) # click
                    
                else:
                    self.logger.error('unable to perform action type "%s"',action['type'])
                    
                # told to stop?
                if self.__evt.is_set(): break
            
            # continue?
            if run_count == repeat: break
            run_count += 1
        
        # all done
        self.logger.info('stopped')





