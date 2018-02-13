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
import tkinter.ttk as ttk
from tkinter import messagebox
import datetime
import queue
from os import path

class MyTkApplication(tk.Tk,MyLoggingBase):
    """The Tk.Frame"""
    DEFAULT_SETTINGS = {'repeat limit':0,
                        'start delay':12,
                        'start variance':0,
                        'action variance':0}
    settings = None
    main_frame = None
    status_bar = None
    
    def __init__(self):
        # init base classes
        MyLoggingBase.__init__(self,name='app')
        tk.Tk.__init__(self)
        
        # load settings
        self.settings = self.DEFAULT_SETTINGS
        for k,v in self.read_file_key_values(self.get_resource_fd('settings.ini')).items():
            try: t = float(v) # is float?
            except ValueError: t = v # must be string
            else:
                if t == int(t): t = int(t) # is int?
            self.settings[k] = t
        
        # setup application window
        self.title(main.__title__) # set title
        self.iconname(main.__title__)
        self.attributes('-topmost', True) # always on top
        self.minsize(width=255,height=1) # set min width so we see full title!
        self.resizable(width=False,height=False) # not resizable
        self.protocol("WM_DELETE_WINDOW", self.on_quit) # bind ALT+F4
        
        # add MenuBar
        menu_bar = MyTkMenuBar(self)
        self.config(menu=menu_bar) #attach to frame
        
        # add StatusBar
        self.status_bar = MyTkStatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # add MainFrame
        self.main_frame = MyTkMainFrame(self)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # Remain invisible while we resize
        #self.withdraw() # invisible #self.transient(self.master)
        #self.transient(self.master)
        #self.update_idletasks() # update geometry
        
        # set title bar icon (causes geo and to show)
        try: self.iconbitmap(self.get_resource_fd('python-icon.ico'))
        except tk.TclError: pass # in ubuntu: _tkinter.TclError: bitmap /.../... not defined
#         self.logger.debug('%r %r %r (%r,%r) -- (%r,%r) %r %r',
#                           self.winfo_ismapped(),
#                           self.winfo_rootx(),
#                           self.winfo_rooty(),
#                           self.winfo_screenwidth(),
#                           self.winfo_screenheight(),
#                           self.winfo_width(),
#                           self.winfo_height(),
#                           self.winfo_reqwidth(),
#                           self.winfo_reqheight()
#                           )
        self.set_status('Ready') # update status
        #self.deiconify() # visible
        
    def not_implemented(self, evt=None):
        """for buttons not yet bound"""
        self.logger.debug('evt:%s',evt)
        self.set_status('Feature not implemented')
        messagebox.showerror('Not Implemented', 'This feature has net yet been built!')
        
    def on_quit(self, evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """run on quit  """
        self.logger.debug('cleaning ...')
        
        # stop recorder if running
        if self.main_frame.recorder:
            #messagebox.showerror('Not Implemented', 'This feature has net yet been built!')
            if self.main_frame.recorder.is_alive():
                self.main_frame.recorder.stop()
                self.main_frame.recorder.join()
        
        # save settings
        saved = self.write_file_key_values(
            self.get_resource_fd('settings.ini'),
            overwrite_file=True, **self.settings)
        if saved: self.logger.debug('settings saved')
        else: self.logger.warning('settings failed to save')
        
        self.quit() # quit!
    
    def set_status(self,msg,*args):
        """set the status"""
        self.status_bar.set_status(msg.format(*args))

class MyTkMenuBar(tk.Menu,MyLoggingBase):
    """menubar for application"""
    
    DEFAULT_ABOUT_TXT = ('By: owns <owns13927@yahoo.com>\n'+
                         '\nVersion: '+main.__version__+
                         '\nRepo: '+main.__repo__+
                         '\nCreated: 2017-03-19'+
                         '\nModified: '+datetime.datetime.fromtimestamp(path.getmtime(__file__)).strftime('%Y-%m-%d')+
                         '')

    def __init__(self, parent):
        MyLoggingBase.__init__(self,name='menubar')
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
        messagebox.showinfo('About '+self.master.title(),self.DEFAULT_ABOUT_TXT)
    
    def tool_test_color(self,evt=None):
        """open mini tool to get color values"""
        self.logger.debug('evt:%s',evt)
        self.master.not_implemented(evt)        
    
class MyTkStatusBar(ttk.Frame,MyLoggingBase):
    """status bar"""
    vars = None

    def __init__(self, parent):
        MyLoggingBase.__init__(self, name='statusbar')
        ttk.Frame.__init__(self, parent)
        
        self.vars = [] # if we want multiple labels
        self.add_section() # add status section
    
    def add_section(self,weight=1):
        index = len(self.vars)
        # create text var
        text_var = tk.StringVar(value='loading ...')
        
        # create label and bind to text var
        ttk.Label(self,
            textvariable=text_var,
            #relief=tk.SUNKEN, #SUNKEN #GROOVE
            background='#ffffff',
            width=1, # stop resizing!
            anchor=tk.W
        ).grid(row=0,column=index,sticky=tk.W+tk.E)
        
        # add var so we can set it's value later
        self.vars.append(text_var)
        
        # set grid weight
        self.grid_columnconfigure(index,weight=weight)
    
    # set values
    def set_text(self, status_index, new_text): self.vars[status_index].set(new_text)
    def set_status(self, new_text): self.vars[0].set(new_text)
        
class MyTkMainFrame(ttk.Frame,MyLoggingBase):
    """main frame - middle bits"""
    
    btn_record = None
    btn_run = None
    LB_MAX_SIZE = 6
    list_actions = None
    
    actions = None
    recorder = None
    recorder_queue = None
    
    def __init__(self, parent):
        MyLoggingBase.__init__(self, name='mainframe')
        ttk.Frame.__init__(self, parent)
        
        #=======================================================================
        # Frame
        #=======================================================================
        # buttons
        self.btn_record = ttk.Button(self,text='Record (Ctrl+Shift+R)',command=self.record)
        self.btn_record.grid(row=0,column=0,sticky=tk.N+tk.E+tk.S+tk.W)
        self.bind_all('<Control-Shift-R>',self.start_recording)
        self.bind_all('<<stop-recording>>',self.stop_recording)
        self.btn_run = ttk.Button(self,text='Run (Ctrl+R)',command=self.run)
        self.btn_run.grid(row=0,column=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.bind_all('<Control-r>',self.run)
        
        self.columnconfigure(0, weight=1) # so resize will fit
        self.columnconfigure(1, weight=1) # so resize will fit
        
        # next action
        lf = ttk.LabelFrame(self,text='Next Action:')
        self.__next_action = tk.StringVar(value='',name='next action')
        ttk.Label(lf,textvariable=self.__next_action,
                 anchor=tk.W,justify=tk.LEFT,width=33
                 ).grid(row=1,column=0,columnspan=2,
                        sticky=tk.N+tk.E+tk.S+tk.W)
        lf.columnconfigure(0, weight=1) # so resize will fit
        lf.grid(row=1,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)
 
        # console
        lf = ttk.LabelFrame(self,text='Console:')
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/ttk-Treeview.html
        self.list_actions = ttk.Treeview(lf,
                                         height=self.LB_MAX_SIZE,
                                         selectmode='none',
                                         show='tree',
                                         takefocus=False)
        # setup columns
        self.list_actions['columns'] = ('ind','text')
        self.list_actions.column('#0',minwidth=0,width=0,stretch=False)
        self.list_actions.column('ind',minwidth=33,width=33,stretch=False)
        self.list_actions.column('text',minwidth=30,width=30,stretch=True)
        self.list_actions.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # add vertical scroll bar https://stackoverflow.com/questions/41877848/python-treeview-scrollbar
        vsb = ttk.Scrollbar(lf,orient='vertical', command=self.list_actions.yview)
        vsb.pack(side=tk.LEFT,fill=tk.Y)
        self.list_actions.config(yscrollcommand=vsb.set)
        
        #lf.columnconfigure(0, weight=1) # so resize will fit
        lf.grid(row=2,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)

#===========================================================================
#--- Record
#===========================================================================
    def record(self,evt=None):
        """ start/stop recording..."""
        if self.btn_record['state'] == tk.DISABLED: return None # stop!
        self.logger.info('clicked - %s ...','stopping' if bool(self.recorder) else 'recording')
        if self.recorder: self.stop_recording(evt)
        else: self.start_recording(evt)

    def start_recording(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """start recording actions"""
        if self.recorder:
            self.logger.warning('tried to start recording while already recording!')
            return # stop!
        
        # prompt for settings
        dlg = MySettingsDialog(parent=self,inputs=self.master.settings)
        if dlg.result is None:
            return # dialog was dismissed
        else:
            self.master.settings.update(dlg.result)
        
        # format and prep
        self.btn_record.config(text=' '.join(
            ['Stop']+self.btn_record['text'].split(' ')[1:]))
        self.btn_run.config(state=tk.DISABLED)
        #self.set_next_action('',to_log=False)
        self.master.set_status('Recorder Active')

        # --- start recorder
        # clear console
        for i in self.list_actions.get_children():
            self.list_actions.delete(i)
        # re-set list of actions
        self.actions = MyInputData()
        # create recorder queue
        self.recorder_queue = queue.Queue()
        # create and start recorder
        self.recorder = MyInputRecorder(root=self,actions_queue=self.recorder_queue)
        self.recorder.start()
        # monitor the queue
        self.after(100,self.handle_record_action)

    def handle_record_action(self):
        # anything in queue to process?
        not_empty = True
        while not_empty:
            try: i = self.recorder_queue.get_nowait()
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
                self.actions.append(i)
                self.recorder_queue.task_done()

        # continue?
        if self.recorder:
            self.after(100,self.handle_record_action)

    def stop_recording(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """stop recording actions"""
        if not self.recorder:
            self.logger.warning('tried to stop recording while not recording!')
            return # stop!
        # format and prep
        self.btn_record.config(text=' '.join(
            ['Record']+self.btn_record['text'].split(' ')[1:]))
        self.btn_run.config(state=tk.NORMAL)
        self.master.set_status('Recorder Stopped') # won't show till after b/c join

        # stop recorder - terminate and stop
        if self.recorder.is_alive():
            self.recorder.stop()
            self.recorder.join()
        self.recorder = None
    
    def add_log(self,msg,*args):
        """ insert text to the log dialog """
        self.list_actions.insert('', 0, open=True, #text=''
                                 values=('{0:03d}'.format(len(self.actions)+1),
                                         msg.format(*args),))
    
#===========================================================================
#--- Run
#===========================================================================
    def run(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """ run currently loaded script..."""
        if self.btn_run['state'] == tk.DISABLED: return None # stop!
        self.logger.info('start')
        
        if self.actions is None: return
        for i in self.actions.to_json():
            print(i)






















    
    
    
            