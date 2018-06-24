#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-19
<desc here>
"""

from packages.pymybase.myloggingbase import MyLoggingBase
import main
from mydata import MyData
from myrecorder import MyRecorder
from myplayer import MyPlayer
from mysettingsdialog import MySettingsDialog
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
import datetime
import queue
import os
from enum import Enum
import json

class State(Enum):
    MENU = 'in menu'
    RECORDING = 'recording'
    RUNNING = 'running'

class MyTkApplication(tk.Tk,MyLoggingBase):
    """The Tk.Frame"""
    DEFAULT_SETTINGS = {'repeat limit':0, # seconds
                        'start delay':12,
                        'start variance':0,
                        'action variance':0}
    settings = None
    main_frame = None
    status_bar = None
    
    actions = None
    
    _state = None
    
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
    
    def start_state(self, state):
        if self._state == None:
            self._state = state
            return True
        else: return False
    
    def can_end_state(self, state):
        return self._state == state
    
    def end_state(self, state):
        if self._state == state:
            self._state = None
            return True
        else:
            self.logger.warning('unable to end state %s - current state %s',
                                state,self._state)
            return False
    
    def get_state(self):
        return self._state
    
    def not_implemented(self, evt=None):
        """for buttons not yet bound"""
        self.logger.debug('evt:%s',evt)
        self.set_status('Feature not implemented')
        messagebox.showerror('Not Implemented', 'This feature has net yet been built!')
        
    def on_quit(self, evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """run on quit  """
        self.logger.debug('cleaning ...')
        
        # stop recorder/player if running
        if self.main_frame.actioner:
            #messagebox.showerror('Not Implemented', 'This feature has net yet been built!')
            if self.main_frame.actioner.is_alive():
                self.main_frame.actioner.stop()
                self.main_frame.actioner.join()
        
        self.main_frame.actions_queue = None
        
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
                         '\nModified: '+datetime.datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%Y-%m-%d')+
                         '')
    __fullname = None # the current actions save file
    __id = None # the id for .master.actions
    
    def __init__(self, parent):
        MyLoggingBase.__init__(self,name='menubar')
        tk.Menu.__init__(self, parent)

        # MenuBar - File
        file_menu = tk.Menu(self,tearoff=0)
        file_menu.add_command(label='New',command=self.check_in_menu(self.new),
                              underline=0,accelerator='Ctrl+N')
        self.bind_all('<Control-n>',self.check_in_menu(self.new))
        file_menu.add_command(label='Open...',command=self.check_in_menu(self.open),
                              underline=0,accelerator='Ctrl+O')
        self.bind_all('<Control-o>',self.check_in_menu(self.open))
        file_menu.add_separator()
        file_menu.add_command(label='Save',command=self.check_in_menu(self.save),
                              underline=0,accelerator='Ctrl+S')
        self.bind_all('<Control-s>',self.check_in_menu(self.save))
        file_menu.add_command(label='Save As ...',command=self.check_in_menu(self.saveAs),
                              accelerator='Ctrl+Shift+S')
        self.bind_all('<Control-Shift-S>',self.check_in_menu(self.saveAs))
        file_menu.add_separator()
        file_menu.add_command(label='Exit',command=self.check_in_menu(parent.on_quit),
                              underline=1,accelerator='Ctrl+Q')
        self.bind_all('<Control-q>',self.check_in_menu(parent.on_quit))
        self.add_cascade(label='File',menu=file_menu,underline=0)

        # MenuBar - Edit
        edit_menu = tk.Menu(self,tearoff=0)
        edit_menu.add_command(label='Text Editor...',command=self.check_in_menu(parent.not_implemented),
                              underline=0,accelerator='Ctrl+T')
        self.bind_all('<Control-t>',self.check_in_menu(parent.not_implemented))
        edit_menu.add_separator()
        edit_menu.add_command(label='Options',command=self.check_in_menu(self.edit_options),
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

    def start_state(self,*args,**keys): return self.master.start_state(*args,**keys)
    def can_end_state(self,*args,**keys): return self.master.can_end_state(*args,**keys)
    def end_state(self,*args,**keys): return self.master.end_state(*args,**keys)
    def get_state(self,*args,**keys): return self.master.get_state(*args,**keys)
#===============================================================================
#--- Menu Bar Actions
#===============================================================================
    def check_in_menu(self, f):
        def check_in_menu(*args,**keys):
            if self.start_state(State.MENU):
                a = f(*args,**keys)
                self.end_state(State.MENU)
                return a
            else:
                self.logger.debug('unable to start %s - in %s',f.__name__, self.get_state())
                return None
        
        return check_in_menu
    
    def edit_options(self,evt=None):
        """open settings dialog and save changes"""
        self.logger.debug('open options dialog by %s','shortcut' if evt else 'click')
        
        dlg = MySettingsDialog(parent=self.master,inputs=self.master.settings)
        if dlg.result is None:
            self.logger.debug('options dismissed')
        else:
            self.master.settings.update(dlg.result)
            self.logger.info('settings updated')
        
    def show_about(self,evt=None):
        """ open the help dialog """
        self.logger.debug('start by %s','shortcut' if evt else 'click')
        messagebox.showinfo('About '+self.master.title(),self.DEFAULT_ABOUT_TXT)
    
    def tool_test_color(self,evt=None):
        """open mini tool to get color values"""
        self.logger.debug('start by %s','shortcut' if evt else 'click')
        self.master.not_implemented(evt)        
    
    def new(self,evt=None):
        self.logger.debug('start by %s','shortcut' if evt else 'click')
        
        if self.master.actions:
            # prompt to clear
            if messagebox.askokcancel(
                'Are you sure?',
                'starting new will clear your current',
                icon=messagebox.WARNING):
                self.logger.debug('confirm')
            else:
                self.logger.debug('cancel')
        else:
            self.logger.debug('no actions to clear')
    
    def open(self,evt=None):
        self.logger.debug('start by %s','shortcut' if evt else 'click')
        
        # check there are actions to save
#         if not self.master.actions and not messagebox.askokcancel(
#                 'Are you sure?',
#                 'the current actions list to be lost if a new file is opened'):
#             return
        
        # get the default or old file selected
        init_fd, init_file = self._get_fd_file()
        
        # prompt for save file
        fullname = filedialog.askopenfilename(
            title='Open'+(' - current recording will be lost!' if self.master.actions else ''),
            parent=self.master,
            initialdir=init_fd,
            initialfile=init_file,
            filetypes = [('text files', '.txt'),('all files', '.*')],
            defaultextension='.txt')
        # if a filename was selected
        if fullname:
            # try to load the fullname
            self.load_script(fullname)
        else: self.logger.debug('save dismissed')
    
    def save(self,evt=None):
        self.logger.debug('start by %s','shortcut' if evt else 'click')
        # check there are actions to save
        if not self.master.actions:
            messagebox.showwarning('Unavailable', 'no actions currently loaded to save.')
            return
        
        # saveAs if no file
        if self._get_fullname() is None: return self.saveAs(evt=evt)
        
        # open save file for writing
        fullname = self._get_fullname()
        with open(fullname,mode='w') as w:
            # save options
            w.write('# settings\n')
            w.write(json.dumps(self.master.settings, sort_keys=True)+'\n')
            
            # save the actions
            w.write('\n# actions\n')
            for a in self.master.actions:
                w.write(json.dumps(a, sort_keys=True)+'\n')
        
        # done!
        self.logger.info('saved to %s',fullname)
        
    def saveAs(self,evt=None):
        self.logger.debug('start by %s','shortcut' if evt else 'click')
        # check there are actions to save
        if not self.master.actions:
            messagebox.showwarning('Unavailable', 'no actions currently loaded to save.')
            return
        
        # get the default or old file selected
        init_fd, init_file = self._get_fd_file()
        
        # prompt for save file
        fullname = filedialog.asksaveasfilename(
            #title='',
            parent=self.master,
            initialdir=init_fd,
            initialfile=init_file,
            filetypes = [('text files', '.txt'),('all files', '.*')],
            defaultextension='.txt')
        # if a filename was selected
        if fullname:
            self.logger.debug('selected "%s"',fullname)
            # set fullname
            self._set_fullname(fullname)
            # do the saving
            self.save(evt=evt)
        else: self.logger.debug('save dismissed')
    
    def load_script(self, fullname):
        self.logger.debug('trying "%s"',fullname)
        
        section = None
        settings = self.master.settings
        actions = MyData()
        try:
            with open(fullname,'r') as r:
                # for each none empty line (removing the \n at the end)
                for ind,line in ((ind,line.rstrip()) 
                                 for ind,line in enumerate(r)
                                 if line.rstrip()):
                    # switch mode?
                    if line == '# settings':
                        section = 'settings'
                    elif line == '# actions':
                        section = 'actions'
                    else:
                        # handle json
                        d = json.loads(line)
                        if section == 'settings': settings.update(d)
                        if section == 'actions':
                            if ('name' in d 
                                and 'pressed' in d
                                and 'time' in d
                                and 'type' in d):
                                actions.append(d)
                            else:
                                raise KeyError('missing an action key at line '+
                                               (ind+1)+': name, pressed, time, type')
        except IOError as e:
            self.logger.warning('IOError! %r',e)
            messagebox.showwarning('IO Error',
                                   'Unable to load file, {0!r}'.format(e))
        except KeyError as e:
            self.logger.warning('KeyError! %r',e)
            messagebox.showwarning('Parsing Error',
                                   'Unable to load file, {0!r}'.format(e))
        except Exception as e:  #pylint: disable=broad-except
            self.logger.warning('error! %r',e)
            messagebox.showwarning('Unhandled Exception',
                                   'Unable to load file, {0}.\n{1}'.format(fullname,e))
        else:
            self.logger.info('file loaded %d actions',len(actions))
            # success - make current
            self.master.settings.update(settings)
            self.master.actions = actions
            self._set_fullname(fullname) # track filename used
            # inform user
            messagebox.showinfo('File loaded',
                                   'script loaded, {0}.'.format(fullname))

#===============================================================================
#--- hidden methods    
#===============================================================================
    def _clear_fullname(self):
        self.__fullname = None
        self.__id = None
        self.master.actions = None
        
    def _get_fullname(self):
        if self.__fullname and self.__id:
            if self.__id == id(self.master.actions):
                return self.__fullname
            else:
                self.__fullname = None
                self.__id = None
        return None
    
    def _get_fd_file(self):
        fullname = self._get_fullname()
        if fullname:
            init_fd = os.path.dirname(fullname)
            init_file = os.path.basename(fullname)
        else:
            # create default folder if needed
            init_fd = self.get_resource_fd('scripts')
            if not os.path.exists(init_fd): os.makedirs(init_fd)
            init_file = 'MyScript.txt'
        return init_fd,init_file
    
    def _set_fullname(self,fullname):
        self.__id = id(self.master.actions)
        self.__fullname = fullname
    

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
    
    actioner = None
    actions_queue = None
    
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

    def start_state(self,*args,**keys): return self.master.start_state(*args,**keys)
    def can_end_state(self,*args,**keys): return self.master.can_end_state(*args,**keys)
    def end_state(self,*args,**keys): return self.master.end_state(*args,**keys)
    def get_state(self,*args,**keys): return self.master.get_state(*args,**keys)
#===========================================================================
#--- Record
#===========================================================================
    def record(self,evt=None):
        """ start/stop recording..."""
        if not self.get_state(): self.start_recording(evt)
        elif self.can_end_state(State.RECORDING): self.stop_recording(evt)
        else: self.logger.warning('cannot record - state is %s',self.get_state())

    def start_recording(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """start recording actions"""
        if not self.start_state(State.RECORDING):
            self.logger.warning('tried to start recording while %s!',self.get_state())
            return # stop!
        
        self.logger.info('start recording by %s ...','shortcut' if evt else 'click')
        
        # prompt for settings
        dlg = MySettingsDialog(parent=self,inputs=self.master.settings)
        if dlg.result is None:
            self.end_state(State.RECORDING)
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
        self.master.actions = MyData()
        # create recorder queue
        self.actions_queue = queue.Queue()
        # create and start recorder
        self.actioner = MyRecorder(root=self,actions_queue=self.actions_queue)
        self.actioner.start()
        # monitor the queue
        self.after(100,self.handle_record_action)

    def handle_record_action(self):
        # stopped?
        if not self.actioner: return # stop
        # anything in queue to process?
        not_empty = True
        while not_empty:
            try: i = self.actions_queue.get_nowait()
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
                self.master.actions.append(i)
                self.actions_queue.task_done()

        # continue?
        if self.actioner:
            self.after(100,self.handle_record_action)

    def stop_recording(self,evt=None): #@UnusedVariable #pylint: disable=unused-argument
        """stop recording actions"""
        if not self.can_end_state(State.RECORDING):
            self.logger.warning('tried to stop recording while %s!',self.get_state())
            return # stop!
        
        self.logger.info('stop recording by %s ...','shortcut' if evt else 'click')
        
        # format and prep
        self.btn_record.config(text=' '.join(
            ['Record']+self.btn_record['text'].split(' ')[1:]))
        self.btn_run.config(state=tk.NORMAL)
        self.master.set_status('Recorder Stopped') # won't show till after b/c join

        # stop recorder - terminate and stop
        if self.actioner and self.actioner.is_alive():
            self.actioner.stop()
            self.actioner.join()
        self.actioner = None
        self.actions_queue = None
        
        self.end_state(State.RECORDING)
    
    def add_log(self,msg,*args):
        """ insert text to the log dialog """
        self.list_actions.insert('', 0, open=True, #text=''
                                 values=('{0:03d}'.format(len(self.master.actions)+1),
                                         msg.format(*args),))
    
#===========================================================================
#--- Run
#===========================================================================
    def run(self,evt=None):
        """ run currently loaded script..."""
        
        # actions to run?
        if not self.master.actions:
            self.logger.warning('no actions to run!')
            messagebox.showwarning('No Actions', 'No actions currently loaded.  Either start a recording or load a script.')
            return # stop
        
        # try to run or stop running
        if not self.get_state(): self.start_running(evt)
        elif self.can_end_state(State.RUNNING): self.stop_running(evt)
        else: self.logger.warning('cannot run - state is %s',self.get_state())
        
    def start_running(self,evt=None):
        """ run currently loaded script..."""
        if not self.master.actions or not self.start_state(State.RUNNING):
            self.logger.warning('tried to start running while %s!',self.get_state())
            return # stop!
        
        self.logger.info('start running by %s ...','shortcut' if evt else 'click')
        
        # format and prep
        self.btn_run.config(text=' '.join(
            ['Stop']+self.btn_run['text'].split(' ')[1:]))
        self.btn_record.config(state=tk.DISABLED)
        #self.set_next_action('',to_log=False)
        self.master.set_status('Player Active')
        
        # --- start recorder
        # clear console
        for i in self.list_actions.get_children():
            self.list_actions.delete(i)
        # create runner queue
        self.actions_queue = queue.Queue()
        # create and start recorder
        self.actioner = MyPlayer(root=self,actions_queue=self.actions_queue,
                                 actions=self.master.actions,settings=self.master.settings)
        self.actioner.start()
        # monitor the queue
        self.after(100,self.handle_run_action)
    
    def handle_run_action(self):
        # stopped?
        if not self.actioner: return # stop
        # anything in queue to process?
        not_empty = True
        while not_empty:
            try: i = self.actions_queue.get_nowait()
            except queue.Empty: not_empty = False
            else:
                # update log
                self.logger.debug('%r',i)
                #self.master.actions[i]
                self.actions_queue.task_done()

        # continue?
        if self.actioner:
            self.after(100,self.handle_record_action)
    
    def stop_running(self,evt=None):
        """ stop running currently loaded script..."""
        if not self.master.actions or not self.can_end_state(State.RUNNING):
            self.logger.warning('tried to stop running while %s!',self.get_state())
            return # stop!
        
        self.logger.info('stop running by %s ...','shortcut' if evt else 'click')
        
        # format and prep
        self.btn_run.config(text=' '.join(
            ['Run']+self.btn_run['text'].split(' ')[1:]))
        self.btn_record.config(state=tk.NORMAL)
        self.master.set_status('Player Stopped') # won't show till after b/c join

        # stop recorder - terminate and stop
        if self.actioner and self.actioner.is_alive():
            self.actioner.stop()
            self.actioner.join()
        self.actioner = None
        self.actions_queue = None
        
        
        self.end_state(State.RUNNING)
        
#===============================================================================
# run main
#===============================================================================
if __name__ == '__main__': main.main()
















    
    
    
            