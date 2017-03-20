"""
@author: Elias Wood (owns13927@yahoo.com)
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
#http://stackoverflow.com/questions/16745507/tkinter-how-to-use-threads-to-preventing-main-event-loop-from-freezing



if __name__ == '__main__':
    from myloggingbase import MyLoggingBase
    MyLoggingBase.init_logging(file_log_lvl=None,show_warning=False)
    logger = MyLoggingBase().logger
    logger.debug('hello world')
    logger.info(MyLoggingBase.get_output_fd())
    
    
    # click w/ mouse
#    from pynput.mouse import Button, Controller #https://pypi.python.org/pypi/pynput
#    import time
#     logger.info('looping...')
#     mouse = Controller()
#     while True:
#         mouse.click(Button.left)
#         time.sleep(0.8)
#     logger.info('done')
    
    from mytkapplication import MyTkApplication
    app = MyTkApplication()
    app.mainloop()
    
