#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-19
<desc here>
"""

from packages.pymybase.myloggingbase import MyLoggingBase
import main
from myinputrecorder import MyInputRecorder
from myinputdata import MyInputData
from mysettingsdialog import MySettingsDialog
import tkinter as tk
#import tkinter.ttk as ttk
from tkinter import messagebox
import datetime
import queue
from os import path

class MyTkApplication(tk.Frame,MyLoggingBase): #pylint: disable=too-many-instance-attributes
    """The Tk.Frame"""
    DEFAULT_TITLE = 'PyCleverClicker'
    DEFAULT_SETTINGS = {'repeat limit':0,
                        'start delay':12,
                        'start variance':0,
                        'action variance':0}
    settings = None
    
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
        # init base classes
        MyLoggingBase.__init__(self)
        tk.Frame.__init__(self, master)
        
        # set title
        self.master.title(title if title else self.DEFAULT_TITLE)
        
        # load settings
        self.settings = self.DEFAULT_SETTINGS
        self.settings.update(
            self.read_file_key_values(self.get_resource_fd('settings.ini')))
        
        # set grid style
        tk.Grid.rowconfigure(self.master, 0, weight=1)
        tk.Grid.columnconfigure(self.master, 0, weight=1)
        self.grid(sticky=tk.N+tk.E+tk.S+tk.W) #self.pack()
        
        # create the frame
        self.create_frame()

        # format application (no resize, always on top, icon)
        self.master.resizable(0,0) # not resizable
        #self.master.call('wm', 'attributes', '.', '-topmost', True)
        self.master.wm_attributes('-topmost', True) # always on top
        # set title bar icon
        try: self.master.iconbitmap(self.get_resource_fd('python-icon.ico'))
        except tk.TclError: pass # in ubuntu: _tkinter.TclError: bitmap /.../... not defined
        
        
#===========================================================================
#--- dummy functions
#===========================================================================
    def not_implemented(self, evt=None):
        """for buttons not yet bound"""
        self.logger.debug('evt:%s',evt)
        self.set_status('Feature not implemented')
        messagebox.showerror('Not Implemented', 'This feature has net yet been built!')

#===========================================================================
#--- clean up!!!
#===========================================================================
    def on_quit(self, evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """run on quit  """
        self.logger.debug('cleaning ...')
        
        # stop recorder if running
        if self.__recorder:
            #messagebox.showerror('Not Implemented', 'This feature has net yet been built!')
            if self.__recorder.is_alive():
                self.__recorder.stop()
                self.__recorder.join()
        
        # save settings
        saved = self.write_file_key_values(
            self.get_resource_fd('settings.ini'),
            overwrite_file=True, **self.settings)
        if saved: self.logger.debug('settings saved')
        else: self.logger.warning('settings failed to save')
        
        # quit!
        self.quit()

#===========================================================================
#--- create entire frame
#===========================================================================
    def create_frame(self):
        """build the frame"""
        # Binds
        self.master.protocol("WM_DELETE_WINDOW", self.on_quit)
        
        # MenuBar
        menu_bar = MyTkMenuBar(self)
        # MenuBar - attach to frame
        self.master.config(menu=menu_bar)

        #=======================================================================
        # Frame
        #=======================================================================
        # buttons
        self.btn_record = tk.Button(self,text='Record (Ctrl+Shift+R)',command=self.record)
        self.btn_record.grid(row=0,column=0,sticky=tk.N+tk.E+tk.S+tk.W)
        self.bind_all('<Control-Shift-R>',self.record)
        self.bind_all('<<stop-recording>>',self.stop_recording)
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
#--- Record
#===========================================================================
    def record(self,evt=None):
        """ start/stop recording..."""
        if self.btn_record['state'] == tk.DISABLED: return None # stop!
        self.logger.info('clicked - %s ...','stopping' if bool(self.__recorder) else 'recording')
        if self.__recorder: self.stop_recording(evt)
        else: self.start_recording(evt)

    def start_recording(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """start recording actions"""
        if self.__recorder:
            self.logger.warning('tried to start recording while already recording!')
            return # stop!
        
        # prompt for settings
        dlg = MySettingsDialog(parent=self.master,inputs=self.settings)
        if dlg.result is None:
            return # dialog was dismissed
        else:
            self.settings.update(dlg.result)
        
        # format and prep
        self.btn_record.config(text=' '.join(
            ['Stop']+self.btn_record['text'].split(' ')[1:]))
        self.btn_run.config(state=tk.DISABLED)
        self.set_next_action('',to_log=False)
        self.set_status('Recorder Active')

        # start recorder
        self.__input_list = MyInputData()
        self.__q = queue.Queue()
        self.__recorder = MyInputRecorder(root=self.master,actions_queue=self.__q)
        self.__recorder.start()
        self.after(100,self.handle_record_action)

    def handle_record_action(self):
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
            self.after(100,self.handle_record_action)

    def stop_recording(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """stop recording actions"""
        if not self.__recorder:
            self.logger.warning('tried to stop recording while not recording!')
            return # stop!
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
#--- Run
#===========================================================================
    def run(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """ run currently loaded script..."""
        if self.btn_run['state'] == tk.DISABLED: return None # stop!
        self.logger.info('start')
        
        if self.__input_list is None: return
        for i in self.__input_list.to_json():
            print(i)

#===========================================================================
#--- update user
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

class MyTkMenuBar(tk.Menu,MyLoggingBase):
    """menubar for application"""
    
    DEFAULT_ABOUT_TXT = ('By: owns <owns13927@yahoo.com>\n'+
                         '\nVersion: '+main.__version__+
                         '\nRepo: '+main.__repo__+
                         '\nCreated: 2017-03-19'+
                         '\nModified: '+datetime.datetime.fromtimestamp(path.getmtime(__file__)).strftime('%Y-%m-%d')+
                         '')

    def __init__(self, parent, name=None):
        MyLoggingBase.__init__(self, name=name)
        tk.Menu.__init__(self, parent)

        # MenuBar - File
        file_menu = tk.Menu(self,tearoff=0)
        file_menu.add_command(label='New',command=parent.not_implemented,
                              underline=0,accelerator='Ctrl+N')
        self.bind_all('<Control-n>',parent.not_implemented)
        file_menu.add_command(label='Open...',command=parent.not_implemented,
                              underline=0,accelerator='Ctrl+O')
        self.bind_all('<Control-o>',parent.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label='Save',command=parent.not_implemented,
                              underline=0,accelerator='Ctrl+S')
        self.bind_all('<Control-s>',parent.not_implemented)
        file_menu.add_command(label='Save As ...',command=parent.not_implemented,
                              accelerator='Ctrl+Shift+S')
        self.bind_all('<Control-Shift-S>',parent.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label='Exit',command=parent.on_quit,
                              underline=1,accelerator='Ctrl+Q')
        self.bind_all('<Control-q>', parent.on_quit)
        self.add_cascade(label='File',menu=file_menu,underline=0)

        # MenuBar - Edit
        edit_menu = tk.Menu(self,tearoff=0)
        edit_menu.add_command(label='Text Editor...',command=parent.not_implemented,
                              underline=0,accelerator='Ctrl+T')
        self.bind_all('<Control-t>',parent.not_implemented)
        edit_menu.add_separator()
        edit_menu.add_command(label='Options',command=self.menu_edit_options,
                              underline=0,accelerator='')
        self.add_cascade(label='Edit',menu=edit_menu,underline=0)

        # MenuBar - Tools
        tool_menu = tk.Menu(self,tearoff=0)
        tool_menu.add_command(label='Test Color...',command=self.tool_test_color,
                              underline=0,accelerator='Shift+T')
        self.bind_all('<Shift-T>',self.tool_test_color)
        self.add_cascade(label='Tools',menu=tool_menu,underline=0)
 
        # MenuBar - Help
        help_menu = tk.Menu(self,tearoff=0)
        help_menu.add_command(label='About',command=self.show_about,underline=0)
        self.add_cascade(label='Help',menu=help_menu,underline=0)

#===============================================================================
#--- Menu Bar Actions
#===============================================================================
    def menu_edit_options(self,evt=None):
        """open settings dialog and save changes"""
        self.logger.debug('open options dialog %s','' if evt is None else evt)
        
        dlg = MySettingsDialog(parent=self.master,inputs=self.master.settings)
        if dlg.result is None:
            self.logger.debug('options dismissed')
        else:
            self.master.settings.update(dlg.result)
            self.logger.info('settings updated')
        
    def show_about(self,evt=None):
        """ open the help dialog """
        self.logger.debug('evt:%s',evt)
        messagebox.showinfo('About '+self.master.master.title(),self.DEFAULT_ABOUT_TXT)
    
    def tool_test_color(self,evt=None):
        """open mini tool to get color values"""
        self.logger.debug('evt:%s',evt)
        self.master.not_implemented(evt)        
    
            
            