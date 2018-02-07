#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Elias Wood <owns13927@yahoo.com>
Created on 2017-03-19
main for application
"""

"""
read screen pixel
http://stackoverflow.com/questions/1997678/faster-method-of-reading-screen-pixel-in-python-than-pil
from ctypes import windll
dc = windll.user32.GetDC(0)
x = 10
y = 10
l = windll.gdi32.GetPixel(dc,x,y)
hexS = hex(l)
print('color at',x,y,'is',hexS)
"""

# simply threading...
#http://stackoverflow.com/questions/16745507/tkinter-how-to-use-threads-to-preventing-main-event-loop-from-freezing pylint: disable=line-too-long

def main():
    """main application"""
    # init logging and get main logger
    from packages.pymybase.myloggingbase import MyLoggingBase
    MyLoggingBase.init_logging(file_log_lvl='DEBUG',file_log_name='pycleverclicker.log')
    logger = MyLoggingBase().logger

    # start app
    logger.info('start')
    from mytkapplication import MyTkApplication
    app = MyTkApplication()
    app.mainloop()
    logger.info('done')

#===============================================================================
# run main
#===============================================================================
if __name__ == '__main__': main()
