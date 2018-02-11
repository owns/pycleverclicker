#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2018-02-10
store,export,import,iter through scripts
"""

from packages.pymybase.myloggingbase import MyLoggingBase
import tkinter as tk
from tkinter.simpledialog import Dialog

class MySettingsDialog(Dialog,MyLoggingBase):
    
    __inputs = None
    __entries = None
    
    def __init__(self,parent,title=None,
                 inputs=None,
                 name=None):
        MyLoggingBase.__init__(self,name=name)
        self.__inputs = inputs
        
        Dialog.__init__(self,parent=parent,title=title)
        
        
    def body(self, master):
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        '''
        Dialog.body(self, master)
        
        # set icon
        try: self.wm_iconbitmap(self.get_resource_fd('python-icon.ico'))
        except tk.TclError: pass # in ubuntu: _tkinter.TclError: bitmap /.../... not defined
        
        # add inputs
        self.__entries = list()
        r = 0
        for k,v in self.__inputs.items():
            tk.Label(master, text=k+':',justify=tk.LEFT).grid(row=r,column=0,sticky=tk.W)
            self.__entries.append(tk.Entry(master))
            self.__entries[r].grid(row=r,column=1)
            
            if v is not None:
                self.__entries[r].insert(0,v)
            
            r += 1
        
        
    def validate(self):
        '''validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        '''
        if Dialog.validate(self) == 0: return 0
        
        # try
        try:
            1/1
        except Exception as e:  #pylint: disable=broad-except
            tk.messagebox.showwarning(
                e.__class__.__name__,
                (e.message if hasattr(e,'message') else e.__class__.__name__) + "\nPlease try again",
                parent = self
            )
            return 0
        else:
            return 1
        
    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''
        Dialog.apply(self)
        