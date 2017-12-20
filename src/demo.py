# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 10:38:43 2017

@author: jc
"""
 
import sys
from PyQt5.QtWidgets import QApplication
import set_param_led_controller
 


if __name__=="__main__": 
        app = QApplication(sys.argv)
        login = set_param_led_controller.Login()
        _thread.start_new_thread(main_thread,(login,))
        login.show()    
        sys.exit(app.exec())
