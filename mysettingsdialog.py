#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2018-02-10
store,export,import,iter through scripts
"""

from packages.pymybase.myloggingbase import MyLoggingBase
import tkinter as tk
import tkinter.ttk as ttk
#from idlelib.tooltip import ToolTip
from tkinter.simpledialog import Dialog

class MySettingsDialog(Dialog,MyLoggingBase):
    
    result = None
    __inputs = None
    __entries = None
    
    def __init__(self,parent,title=None,
                 inputs=None,
                 name=None):
        MyLoggingBase.__init__(self,name=name)
        self.__inputs = inputs.copy()
        
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
        self.__entries = dict()
        first_key = None
        r = 0
        for k,v in self.__inputs.items():
            # get first entry added so we can set that to have focus
            if first_key is None: first_key = k
            
            # create label
            ttk.Label(master, text=k+':',justify=tk.LEFT).grid(row=r,column=0,sticky=tk.W)
            
            # create entry
            e = ttk.Entry(master,width=9)
            e.grid(row=r,column=1)
            # set default input if any
            if v is not None: e.insert(0, v)
            # add to list
            self.__entries[k] = e
            
            # next row!
            r += 1
        
        # set focus to first entry
        if self.__entries: return self.__entries[first_key]
    
    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''
        #Dialog.buttonbox(self)
        
        # override to use ttk buttons!
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.bind("<KeyRelease-Return>", self.ok) #<Return>
        self.bind("<Escape>", self.cancel)

        box.pack()
     
    def validate(self):
        '''validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        '''
        if Dialog.validate(self) == 0: return 0
        
        for k,entry in self.__entries.items():
            s = entry.get()
            
            # validate if needed
            if self.__inputs[k] is not None and self.__inputs[k] != s:
                # validate data type
                t = type(self.__inputs[k])
                try:
                    v = t(s)
                except ValueError as e:
                    # failed!
                    tk.messagebox.showwarning(
                        e.__class__.__name__,
                        "'{0}' must be of type '{1}'!\nPlease try again".format(k,t.__name__),
                        parent = self
                    )
                    return 0
                else:
                    # good to go, override default with value
                    self.__inputs[k] = v
        
        # passed all validation! - 'apply' to result
        self.result = self.__inputs
        return 1
        
    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        '''
        Dialog.apply(self)
        