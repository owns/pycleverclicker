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

CAN GET SCREEN COLOR!!!
import win32gui
import win32api
import time

def get_pixel_colour(i_x, i_y):
    i_desktop_window_id = win32gui.GetDesktopWindow()
    i_desktop_window_dc = win32gui.GetWindowDC(i_desktop_window_id)
    long_colour = win32gui.GetPixel(i_desktop_window_dc, i_x, i_y)
    i_colour = int(long_colour)
    return (i_colour & 0xff), ((i_colour >> 8) & 0xff), ((i_colour >> 16) & 0xff)

def printPos(x,y,r,g,b):
    print "at ({},{}): {}, {}, {}".format(x,y,r,g,b)
    
def wait(t):
    while t>0:
        print t
        time.sleep(1)
        t -= 1


# some fun!!!

#xMax = win32api.GetSystemMetrics(0)
#yMax = win32api.GetSystemMetrics(1)

#print get_pixel_colour((xMax-1)/2,(yMax-1)/2) # middle pixel color

# every 2 seconds, output the position and color of the mouse
while True:
    x,y = win32api.GetCursorPos()
    r,g,b = get_pixel_colour(x,y)
    printPos(x,y,r,g,b)
    wait(2)
"""

# simply threading...
#http://stackoverflow.com/questions/16745507/tkinter-how-to-use-threads-to-preventing-main-event-loop-from-freezing pylint: disable=line-too-long
__version__ = '0.1.0'
__repo__ = 'https://github.com/owns/pycleverclicker/'

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
