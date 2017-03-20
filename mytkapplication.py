"""
@author: owns
Created on 2017-03-19
<desc here>
"""

import tkinter as tk
from myloggingbase import MyLoggingBase

class MyTkApplication(tk.Frame,MyLoggingBase):
    def __init__(self, master=None):
        MyLoggingBase.__init__(self)
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        
    def on_quit(self,evt=None):
        """run on quit  """
        self.logger.debug('cleaning ...')
        
    def createWidgets(self):
        #=======================================================================
        # Binds
        #=======================================================================
        self.bind('<Destroy>',self.on_quit)
        
        #=======================================================================
        # MenuBar
        #=======================================================================
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar,tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.master.destroy)
        menubar.add_cascade(label="File",menu=filemenu)
        self.master.config(menu=menubar)
        
        #=======================================================================
        # Buttons and Textboxes
        #=======================================================================
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.QUIT = tk.Button(self, text="QUIT", fg="red",command=self.master.destroy)
        self.QUIT.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")