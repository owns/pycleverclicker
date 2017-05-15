#!/usr/bin/env python3
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-26
store,export,import,iter through scripts
"""

#import time
from pymybase.myloggingbase import MyLoggingBase

class MyInputData(list,MyLoggingBase):
    """class to hold input value - to be passed around"""

    def __init__(self, *args,**keys):
        MyLoggingBase.__init__(self,*args,**keys)

        list.__init__(self,*args,**keys)

    def to_str(self):
        """serialize"""
        raise NotImplementedError()

    def from_string(self):
        """de-serialize"""
        raise NotImplementedError()

    def __str__(self, *args, **kwargs):
        """see to_str"""
        return MyLoggingBase.__str__(self, *args, **kwargs)
    