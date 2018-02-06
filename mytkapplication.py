#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-19
<desc here>
"""

import tkinter as tk
from tkinter import messagebox
import queue
from packages.pymybase.myloggingbase import MyLoggingBase
from myinputrecorder import MyInputRecorder
from myinputdata import MyInputData

class MyTkApplication(tk.Frame,MyLoggingBase): #pylint: disable=too-many-instance-attributes
    """The Tk.Frame"""
    DEFAULT_TITLE = 'PyCleverClicker'
    DEFAULT_ABOUT_TXT = ('By: owns <owns13927@yahoo.com>\n'+
                         'Created: 2017-03-19\n'+
                         'Modified: 2018-02-06\n'+
                         '')
    __status = None
    __next_action = None
    __log = None
    __lb = None
    LB_MAX_SIZE = 6

    __recorder = None
    __q = None
    __input_list = None
    __running = False

    def __init__(self, master=None,title=None):
        MyLoggingBase.__init__(self)
        tk.Frame.__init__(self, master)
        self.master.title(title if title else self.DEFAULT_TITLE)

        tk.Grid.rowconfigure(self.master, 0, weight=1)
        tk.Grid.columnconfigure(self.master, 0, weight=1)
        self.grid(sticky=tk.N+tk.E+tk.S+tk.W) #self.pack()
        self.create_frame()

        self.master.resizable(0,0) # not resizable
        self.master.call('wm', 'attributes', '.', '-topmost', True) # always on top
        # set title bar icon
        try: self.master.iconbitmap(self.get_resource_fd('python-icon.ico'))
        except tk.TclError: pass # in ubuntu: _tkinter.TclError: bitmap /.../... not defined

    #===========================================================================
    # dummy functions
    #===========================================================================
    def not_implemented(self, evt=None):
        """for buttons not yet bound"""
        self.logger.debug('evt:%s',evt)
        self.set_status('Feature not implemented')
        messagebox.showerror('Not Implemented', 'This feature has net yet been built!')

    #===========================================================================
    # Clean up!!!
    #===========================================================================
    def on_quit(self, evt=None): #pylint: disable=unused-argument
        """run on quit  """
        self.logger.debug('cleaning ...')
        if self.__recorder:
            if self.__recorder.is_alive():
                self.__recorder.stop()
                self.__recorder.join()

    #===========================================================================
    # createFrame - build menu bar
    #===========================================================================
    def __create_menubar(self):
        """create and add menubar"""
        menu_bar = tk.Menu(self.master)

        # MenuBar - File
        file_menu = tk.Menu(menu_bar,tearoff=0)
        file_menu.add_command(label='New',command=self.not_implemented,
                              underline=0,accelerator='Ctrl+N')
        self.bind_all('<Control-n>',self.not_implemented)
        file_menu.add_command(label='Open...',command=self.not_implemented,
                              underline=0,accelerator='Ctrl+O')
        self.bind_all('<Control-o>',self.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label='Save',command=self.not_implemented,
                              underline=0,accelerator='Ctrl+S')
        self.bind_all('<Control-s>',self.not_implemented)
        file_menu.add_command(label='Save As ...',command=self.not_implemented,
                              accelerator='Ctrl+Shift+S')
        self.bind_all('<Control-Shift-S>',self.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label='Exit',command=self.master.destroy,
                              underline=1,accelerator='Ctrl+Q')
        self.bind_all('<Control-q>',self.on_quit)
        menu_bar.add_cascade(label='File',menu=file_menu,underline=0)

        # MenuBar - Edit
        edit_menu = tk.Menu(menu_bar,tearoff=0)
        edit_menu.add_command(label='Text Editor...',command=self.not_implemented,
                              underline=0,accelerator='Ctrl+T')
        self.bind_all('<Control-t>',self.not_implemented)
        edit_menu.add_separator()
        edit_menu.add_command(label='Options',command=self.not_implemented,
                              underline=0,accelerator='')
        menu_bar.add_cascade(label='Edit',menu=edit_menu,underline=0)

        # MenuBar - Tools
        tool_menu = tk.Menu(menu_bar,tearoff=0)
        tool_menu.add_command(label='Test Color...',command=self.tool_test_color,
                              underline=0,accelerator='Shift+T')
        self.bind_all('<Shift-T>',self.tool_test_color)
        menu_bar.add_cascade(label='Tools',menu=tool_menu,underline=0)

        # MenuBar - Help
        help_menu = tk.Menu(menu_bar,tearoff=0)
        help_menu.add_command(label='About',command=self.show_about,underline=0)
        menu_bar.add_cascade(label='Help',menu=help_menu,underline=0)

        # MenuBar - attach to frame
        self.master.config(menu=menu_bar)

    def create_frame(self):
        """build the frame"""
        #=======================================================================
        # Binds
        #=======================================================================
        self.bind('<Destroy>',self.on_quit)

        #=======================================================================
        # MenuBar
        #=======================================================================
        self.__create_menubar()

        #=======================================================================
        # Frame
        #=======================================================================
        # buttons
        self.btn_record = tk.Button(self,text='Record (Ctrl+Shift+R)',command=self.record)
        self.btn_record.grid(row=0,column=0,sticky=tk.N+tk.E+tk.S+tk.W)
        self.bind_all('<Control-Shift-R>',self.record)
        self.btn_run = tk.Button(self,text='Run (Ctrl+R)',command=self.run)
        self.btn_run.grid(row=0,column=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.bind_all('<Control-r>',self.run)

        # next action
        tlf = tk.LabelFrame(self,text='Next Action:')
        tlf.columnconfigure(0, weight=1) # so resize will fit
        tlf.grid(row=1,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)
        self.__next_action = tk.StringVar(value='',name='next action')
        tk.Label(tlf,textvariable=self.__next_action,
                 anchor=tk.W,justify=tk.LEFT,width=33
                 ).grid(row=1,column=0,columnspan=2,
                        sticky=tk.N+tk.E+tk.S+tk.W)

        # console
        tlf = tk.LabelFrame(self,text='Console:')
        tlf.columnconfigure(0, weight=1) # so resize will fit
        tlf.grid(row=2,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)
        self.__lb = tk.Listbox(tlf,height=self.LB_MAX_SIZE)
        self.__lb.grid(row=2,column=0,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)
        self.__lb.config(state=tk.DISABLED)
        # status bar
        self.__status = tk.StringVar(value='waiting ...',name='status bar')
        tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                 textvariable=self.__status).grid(row=3,column=0,columnspan=2,
                                                  sticky=tk.N+tk.E+tk.S+tk.W)

        # resizable
        for row in range(3):
            tk.Grid.rowconfigure(self, row, weight=1)
            for col in range(2):
                tk.Grid.columnconfigure(self, col, weight=1)

        self.set_status('Ready')

    #===========================================================================
    # Record
    #===========================================================================
    def record(self,evt=None):
        """ start/stop recording..."""
        if self.btn_record['state'] == tk.DISABLED: return None # stop!
        self.logger.info('clicked recording:%s',bool(self.__recorder))
        if self.__recorder: self._stop_recording(evt)
        else: self._start_recording(evt)

    def _start_recording(self,evt=None): #pylint: disable=unused-argument
        if self.__recorder: raise RuntimeError('tried to start recording while already recording!')
        # format and prep
        self.btn_record.config(text=' '.join(
            ['Stop']+self.btn_record['text'].split(' ')[1:]))
        self.btn_run.config(state=tk.DISABLED)
        self.set_next_action('',to_log=False)
        self.set_status('Recorder Active')

        # start recorder
        self.__input_list = MyInputData()
        self.__q = queue.Queue()
        self.__recorder = MyInputRecorder(actions_queue=self.__q)
        self.__recorder.start()
        self.after(100,self._handle_record_action)

    def _handle_record_action(self):
        # anything in queue to process?
        not_empty = True
        while not_empty:
            try: i = self.__q.get_nowait()
            except queue.Empty: not_empty = False
            else:
                # log to console
                if i['type'] == 'mouse':
                    self.add_log('{0:.3f} {1} click at {2!s}',
                                 i['time'],i['name'],i['pos']) # do work
                else:
                    self.add_log('{0:.3f} {1} released after {2:.1f}',
                                 i['time'],i['name'],i['pressed']) # do work
                # add to list
                self.__input_list.append(i)
                self.__q.task_done()

        # continue?
        if self.__recorder:
            self.after(100,self._handle_record_action)

    def _stop_recording(self,evt=None): #pylint: disable=unused-argument
        if not self.__recorder: raise RuntimeError('tried to stop recording while not recording!')
        # format and prep
        self.btn_record.config(text=' '.join(
            ['Record']+self.btn_record['text'].split(' ')[1:]))
        self.btn_run.config(state=tk.NORMAL)
        self.set_status('Recorder Stopped') # won't show till after b/c join

        # stop recorder - terminate and stop
        if self.__recorder.is_alive():
            self.__recorder.stop()
            self.__recorder.join()
        self.__recorder = None

    #===========================================================================
    # Run
    #===========================================================================
    def run(self,evt=None): #pylint: disable=unused-argument
        """ run currently loaded script..."""
        if self.btn_run['state'] == tk.DISABLED: return None # stop!
        self.logger.info('start')

    #===========================================================================
    # Edit > Text Editor...
    #===========================================================================
    def open_text_editor(self,evt=None):
        """open current script in the text editor"""
        self.logger.debug('evt:%s',evt)
        self.not_implemented(evt)

    #===========================================================================
    # Tools > ...
    #===========================================================================
    def tool_test_color(self,evt=None):
        """open mini tool to get color values"""
        self.logger.debug('evt:%s',evt)
        self.not_implemented(evt)

    #===========================================================================
    # Help > About
    #===========================================================================
    def show_about(self,evt=None):
        """ open the help dialog """
        self.logger.debug('evt:%s',evt)
        messagebox.showinfo('About '+self.master.title(),self.DEFAULT_ABOUT_TXT)

    #===========================================================================
    # update user
    #===========================================================================
    def add_log(self,msg,*args):
        """ insert text to the log dialog """
        self.__lb.config(state=tk.NORMAL)
        self.__lb.insert(0,msg.format(*args))
        size = self.__lb.size()
        if size > self.LB_MAX_SIZE: self.__lb.delete(self.LB_MAX_SIZE, size-1)
        self.__lb.config(state=tk.DISABLED)

    def set_next_action(self,msg,*args,to_log=True):
        """ set the next action text """
        if to_log: self.add_log(self.__next_action.get()) # add last action to log
        self.__next_action.set(msg.format(*args)) # prep

    def set_status(self,msg,*args):
        """set the status"""
        self.__status.set(msg.format(*args))


























