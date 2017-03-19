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

if __name__ == '__main__':
    from myloggingbase import MyLoggingBase
    MyLoggingBase.init_logging(file_log_lvl=None,show_warning=False)
    logger = MyLoggingBase().logger
    logger.debug('hello world')
    logger.info(MyLoggingBase.get_output_fd())
    
    #import pyautogui # https://github.com/asweigart/pyautogui
    #pyautogui.PAUSE = 0
    #pyautogui.moveTo(10,10)
    
    from mytkapplication import MyTkApplication
    #root = tk.Tk()
    app = MyTkApplication()#master=root)
    #app.mainloop()
    
