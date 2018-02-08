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

class MyInputRecorder(Thread,MyLoggingBase):
    """handle recording mouse and keyboard input"""

    __continue_running = True
    __queue = None
    __stop_fn = None
    __time_lock = None
    __key_lock = None
    __pressed_keys = None
    __last_time = None
    log_clicks = True
    log_keys = True
    ignore_key_press = False # track time a key is pressed
    
    __is_shift = None
    
    IGNORE_KEYS = (keyboard.Key.shift,keyboard.Key.shift_l,keyboard.Key.shift_r,
                   keyboard.Key.ctrl,keyboard.Key.ctrl_l,keyboard.Key.ctrl_r,
                   keyboard.Key.alt,keyboard.Key.alt_gr,keyboard.Key.alt_l,keyboard.Key.alt_r,
                   keyboard.Key.cmd,keyboard.Key.cmd_l,keyboard.Key.cmd_r)

    def __init__(self,actions_queue,stop_fn,*args,**keys):
        MyLoggingBase.__init__(self,*args,**keys)
        Thread.__init__(self,*args,**keys)

        self.__queue = actions_queue
        self.__stop_fn = stop_fn
        self.__time_lock = Lock()
        self.__key_lock = Lock()

    #===========================================================================
    # on_click
    #===========================================================================
    def on_click(self,x_pos,y_pos,button,pressed):
        """handle mouse click events"""
        if not self.__continue_running: return False # stop
        if self.log_clicks: self.logger.debug('mouse %s click %s at [%s,%s]',
                button.name,'pressed' if pressed else 'released',x_pos,y_pos)
        if not pressed: # only trigger releases (up)
            with self.__time_lock: #pylint: disable=not-context-manager
                new_time = time.time()
                if not self.__last_time: self.__last_time = new_time
                self.__queue.put_nowait(dict(type='mouse',name=button.name,
                                             pos=(x_pos,y_pos),time=new_time-self.__last_time))
                #self.__queue.put_nowait('{0!s} click at {1!s}'.format(button.name,(x,y)))
                self.__last_time = new_time

    #===========================================================================
    # on_press
    #===========================================================================
    def on_press(self,key):
        """handle key press"""
        if not self.__continue_running: return False # stop listener
        
        if key == keyboard.Key.shift: self.__is_shift = True
        
        if self.ignore_key_press: return None # do nothing

        # valid key (we want)?
        if key in keyboard.Key:
            if key in self.IGNORE_KEYS: return None # stop
        else:
            k = key.char
            if not k.isalnum(): # or k != k.lower():
                if self.__is_shift and key == keyboard.KeyCode(char='\x12'): #ctrl+r
                    #TODO: send button evt?
                    self.logger.warning('needs work!!!')
                    return None # stop listener
                self.logger.warning('invalid key %r',key)
                return None # stop


        # track time when pressed
        name =  key.char if hasattr(key,'char') else key.name
        with self.__key_lock: #pylint: disable=not-context-manager
            cur_time = time.time()
            set_time = self.__pressed_keys.setdefault(name,cur_time)
        
        # if we're logging keys and this is the first time it's been pressed, log it!
        if self.log_keys and cur_time == set_time:
            self.logger.debug('key %s pressed',key.name if hasattr(key,'name') else key.char)

    #===========================================================================
    # on_release
    #===========================================================================
    def on_release(self,key):
        """handle key release"""
        if not self.__continue_running: return False # stop
        
        if key == keyboard.Key.shift: self.__is_shift = False
        
        # valid key (we want)?
        if key in keyboard.Key:
            if key in self.IGNORE_KEYS: return None # stop
        else:
            k = key.char
            if not k.isalnum(): # or k != k.lower():
                self.logger.warning('invalid key %r',key)
                return None # stop

        if self.log_keys:
            self.logger.debug('key %s released',key.name if hasattr(key,'name') else key.char)

        with self.__time_lock: #pylint: disable=not-context-manager
            #  name (unique name) of key pressed
            name=key.char if hasattr(key,'char') else key.name
            # time sense last action?
            new_time = time.time()
            if not self.__last_time: self.__last_time = new_time
            # how long was it pressed?
            if self.ignore_key_press: pressed = 0
            else:
                with self.__key_lock: #pylint: disable=not-context-manager
                    pressed = new_time - self.__pressed_keys.pop(name,new_time)
            # add to queue
            self.__queue.put_nowait(dict(type='type',time=new_time-self.__last_time,
                                         pressed=pressed,name=name))
            # store time for next action
            self.__last_time = new_time

    #===========================================================================
    # STOP
    #===========================================================================
    def stop(self):
        """ start stopping ..."""
        self.logger.info('told to stop')
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

        self.logger.info('stopped')





