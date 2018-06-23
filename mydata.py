#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-26
store,export,import,iter through scripts
"""

import json
from packages.pymybase.myloggingbase import MyLoggingBase

class MyData(list,MyLoggingBase):
    """class to hold input value - to be passed around"""

    def __init__(self, *args,**keys):
        MyLoggingBase.__init__(self,*args,**keys)

        list.__init__(self,*args,**keys)

    def to_json(self):
        """serialize"""
        for i in self:
            yield json.dumps(i, sort_keys=True, separators=(',', ':'))

    def from_json(self, s):
        """de-serialize"""
        raise NotImplementedError()

    def __str__(self, *args, **kwargs):
        """see to_str"""
        return MyLoggingBase.__str__(self, *args, **kwargs)
    