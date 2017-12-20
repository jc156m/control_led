# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 16:32:50 2017

@author:  

qtCreatorFile = "set_le_controller.ui" # Enter file here.
"""     
############
#   self.pushButtonOK.clicked.connect(self.slotLogin)
#  self.pushButtonCancle.clicked.connect(self.slotCancle)

import sys,os
from PyQt5.QtWidgets import ( QMainWindow,QMessageBox)
#重点和秘诀就在这里，大家注意看
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject
import socket 
import time
import threading
import codecs
import struct
import crc16

FALSE = 0
TRUE = 1

MIN_LEN = 30
BUFFSIZE = 610

exit_flag = 0
m_socket = 0 
connect_flag = 0
ip_addr = ""
ip_port = 0
first_login = 1
login = 0
Lumin_flag = 0
Rate_flag = 0
recv_flag = 0
total_data=[]
threadLock = threading.Lock()
crc = crc16.CRC_16()
Lumin_buff = [0x68, 0x06, 0x03 ,0x03 ,0x0B ,0x00, 0x00, 0x10, 0x00, 0x01, 0x00, 0x01, 0x02, 0x00 ,0x11 ,0x6A, 0x1D,0x00] 
Rate_buff =  [0x68, 0x06, 0x03 ,0x03 ,0x0B ,0x00 ,0x00 ,0x10 ,0x00 ,0x05 ,0x00 ,0x01 ,0x02 ,0x00 ,0xAA ,0x2B ,0xEA,0x00]
class ChangeStatus(QObject):
    status_signal = pyqtSignal()
    connect_signal = pyqtSignal()
    reconnect_signal = pyqtSignal()

status_s = ChangeStatus()

class Login(QMainWindow):
    """登录窗口"""
    global status_s
    global connect_signal
    def __init__(self, *args):
        super(Login, self).__init__(*args)
        
        if getattr(sys,'frozen',False):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        loadUi(bundle_dir+'\set_le_controller.ui', self)   #看到没，瞪大眼睛看
        self.label_result.hide()       
        self.Button_Lumin.clicked.connect(self.slotLumin)
        self.Button_Rate.clicked.connect(self.slotRate)
        self.Button_Connect.clicked.connect(self.slotConnect)
        self.text_ip_1.setText('192')
        self.text_ip_2.setText('168')
        self.text_ip_3.setText('0')
        self.text_ip_4.setText('118')
        self.text_ip_port.setText('8500') 
        status_s.status_signal.connect(self.setStatus)
        status_s.connect_signal.connect(self.setConnectTrue)
        status_s.reconnect_signal.connect(self.setreConnectFalse)       
    def slotLumin(self):
        global Lumin_flag
        self.text_result.setText('')
        if connect_flag:
            Lumin_buff[14] = self.Box_Lumin.value()
            m_crc = crc.createcrc(Lumin_buff[6:15])
            Lumin_buff[15] = (m_crc>>8&0xff)
            Lumin_buff[16] = (m_crc&0xff)
            crc.addcheck(Lumin_buff)        
            Lumin_flag = 1
       # self.text_result.setText(str(self.Box_Lumin.value()))
 

    def slotRate(self): 
        global Rate_flag
        self.text_result.setText('')  
        if connect_flag:
            Rate_buff[14] = self.Box_Rate.value()
            m_crc = crc.createcrc(Rate_buff[6:15])
            Rate_buff[15] = (m_crc>>8&0xff)
            Rate_buff[16] = (m_crc&0xff)
            crc.addcheck(Rate_buff)        
            Rate_flag = 1
        #QMessageBox.critical(self,"cuowu","请输入订单号,点击OK进入系统!")
        #self.label_result.show()
 
        
    def slotConnect(self):
        global connect_flag
        global ip_addr 
        global ip_port
        ip_addr = (self.text_ip_1.toPlainText() +'.' + self.text_ip_2.toPlainText() +'.' )
        ip_addr += self.text_ip_3.toPlainText() + '.'
        ip_addr += self.text_ip_4.toPlainText()
        ip_port = int(self.text_ip_port.toPlainText() )
        connect_flag = 1
        self.Button_Connect.setEnabled(False)
        
    def setStatus(self):
            self.text_result.setText("success")
            
    def setConnectTrue(self):
            self.Button_Connect.setEnabled(True)
            
    def setreConnectFalse(self):
            self.Button_Connect.setEnabled(False) 
            
    def closeEvent(self,event):
        global exit_flag
        exit_flag = 1
        time.sleep(2)
 
class recvThread (threading.Thread):
    def __init__(self,threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    def run(self):
        recvdata()        
        
def recvdata():
    global total_data
    global threadLock 
    global m_socket
    global connect_flag
    global status_s
    global exit_flag
    while(connect_flag):
        if exit_flag:
            connect_flag = 0
            break
        try:
            data = m_socket.recv(BUFFSIZE)
        except socket.timeout:
            continue
        except OSError:
            print('os error')
            break
        #print(codecs.encode(data,'hex'))
        
   #     print('xxx')    
        if data:
            threadLock.acquire()
            total_data.append(str(codecs.encode(data,'hex')))
            threadLock.release()
        else:
            connect_flag = 0
            status_s.connect_signal.emit()
            print('empty')
            break

        time.sleep(0.01)
  
    
    
        
def checkframe(temp_buf):
    global recv_flag
    global exit_flag
    temp_str = ''.join(temp_buf)
   # print('&&'+temp_str[0:3])
  #  print(len(temp_str))
 #   print('@@@'+temp_str)
    find = 0
    buf_len = len(temp_str)
    while (0 == find) and temp_str:
        if exit_flag:
            break        
        
        if(len(temp_str)  < MIN_LEN):
            temp_buf.clear()
            temp_buf.append(temp_str)
            return FALSE        
        if(('68' == temp_str[0:2]) and ('06' == temp_str[2:4]) and ('04' == temp_str[4:6]) and ('04' == temp_str[6:8]) and ('08' == temp_str[8:10]) and ('01' == temp_str[22:24])):
            find = TRUE
            recv_flag = 1
            break
        else:
            buf_len -= 1
            temp_str = temp_str[1:]
 #   print('find %d'%find)
    if find:
        temp_buf.clear()
        if (len(temp_str) > 33):
            temp_buf.append(temp_str[33:])
 
def dataSwitch(data):
 #   print(data)
    str1 = struct.pack('%dB'%(len(data)),*data)
    return str1
    

def main_thread():
    global total_data
    global recv_flag
    global threadLock
    global m_socket
    global connect_flag
    global first_login
    global status_s
    global Lumin_flag 
    global Rate_flag 
    
    temp_data = []
    print("main thrad")
    myrecvthread = recvThread(2)
    while True:
        if exit_flag:
            m_socket.close()
            if myrecvthread:
                del myrecvthread
            break
        
        if ((0 == connect_flag) and first_login):
            time.sleep(0.01)
            continue
        first_login = 0
        print('#%s %d'%(ip_addr,ip_port))         
        time.sleep(1)

        m_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
        m_socket.setblocking(0)
        m_socket.settimeout(0.03)
        try:
            m_socket.connect((ip_addr,ip_port))
        except socket.timeout as e:
             print ("error1 请重连！")
             m_socket.close()
             status_s.connect_signal.emit()
             continue
        except ConnectionRefusedError:
            print('error2 please reconnect')
            m_socket.close()
            status_s.connect_signal.emit()            
            continue
         
        status_s.reconnect_signal.emit()
      #  print('connect')
        

        connect_flag = 1
        try:
            myrecvthread.start()
        except:
            m_socket.close()
            del myrecvthread
            myrecvthread = recvThread(2)
           # print("myrecv")
            continue

        
        while connect_flag:
            if exit_flag:
                m_socket.close()
                del myrecvthread
                break
            
            time.sleep(0.02)
            
            if len(total_data) > 0:
                threadLock.acquire()
                temp_data.append(''.join(total_data))
                total_data.clear()
                threadLock.release()

            if len(''.join(temp_data)) >= MIN_LEN:
                checkframe(temp_data)               
            if recv_flag:
                status_s.status_signal.emit()
                recv_flag = 0
                print('status_signal emit')
            if Lumin_flag:
                m_socket.send(dataSwitch(Lumin_buff))
                Lumin_flag = 0
            if Rate_flag:
                m_socket.send(dataSwitch(Rate_buff))
                Rate_flag = 0
            
            
      
class myThread (threading.Thread):
    def __init__(self,threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID   
    def run(self):
        main_thread()
            
        
            
if __name__=="__main__": 
    app = QApplication(sys.argv)
    login = Login()
    thread1 = myThread(1)
    thread1.setDaemon(True)
    thread1.start()
    login.show()    
    sys.exit(app.exec())                 