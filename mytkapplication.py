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
        
        
        self.logger.info(MyLoggingBase.get_output_fd())

    def createWidgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.QUIT = tk.Button(self, text="QUIT", fg="red",command=self.quit)
        self.QUIT.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")