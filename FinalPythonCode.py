from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.animation import Animation
import multiprocessing as mp
from multiprocessing import Process
import binascii
import struct
import time
from bluepy import btle
from bluepy.btle import UUID
import xlsxwriter
from xlsxwriter import*
import os.path
import string
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import math
import time
import random

#Global variables
dev_R = btle.Peripheral(None)      #Right foot arduino
dev_L = btle.Peripheral(None)      #left foot arduino
bt_power = 0
#Rows in spread sheet1 for data from right foot
r_1R = 1
#Rows in spread sheet1 for data from left foot
r_1L = 1 
#Rows in spread sheet2
r_2 = 1
#process variables
p1 = None
p2 = None

#Worksheet
wb = None

#Sheets
sheet1 = None
sheet2 = None


def disconnect():
    global dev_R
    global dev_L
    dev_R.disconnect()
    dev_L.disconnect()
    return
    
def make_workbook():
    save_path = '/media/pi/LEXAR'
    #Variable used to name file number
    n=1
    #Searches for exixting file of same name
    match = os.path.exists("/media/pi/LEXAR/Power_phase Session " + str(n)+".xlsx")
    
    while match==True:
        n=n+1
        match = os.path.exists("/media/pi/LEXAR/Power_phase Session " + str(n)+".xlsx")
        
    #Names File
    name_of_file = "Power_phase Session " + str(n) 
    completeName = os.path.join(save_path, name_of_file+".xlsx")
    
    # Workbook is created
    global wb
    wb = xlsxwriter.Workbook(completeName)
    
    return

    
def handle_data(a,data):
    def add_to_graph(a,data):
        if (a == 0):
        
            print("Right data received")
            global r_1R
            global sheet1
            sheet1.write(r_1R, 0, data)
            
        
        else:
            
            print("Left data received")
            global r_1L
            global sheet1
            sheet1.write(r_1L, 2, data)
        
        
    def display_data(a, data):
        if (a == 0):
            j = data
            pi = math.pi
            origin = [0], [0] # origin point
            fig = plt.figure()
            widget = fig
            
            arg_i = (pi*i)/180
            x = j*math.sin(arg_i)
            y = j*math.cos(arg_i)
            V = np.array([[x,y]])
            plt.quiver(*origin, V[:,0], V[:,1], color=['b'], scale=1500)
            
            anim = Animation(x=100, y=100)
            start.anim.start(widget)
    
        
    
    if __name__ == '__main__':
        p3 = Process(target = add_to_graph, args =(a,data))
        p3.start()
        p4 = Process(target = display_data, args = (a, data))
        p4.start()
    return

def data_processing():
    global bt_power
    bt_power = 1
    def right():
        global dev_R
        dev_R.connect("F4:5E:AB:B0:8E:CC", )
        global bt_power
    
        class MyDelegate(btle.DefaultDelegate):
            def __init__(self):
                btle.DefaultDelegate.__init__(self)

            def handleNotification(self, cHandle, data):
                data = int(data)
                print("A notification was received from right: " + str(data))
                a = 0
                handle_data(a,data)
                global r_1R
                r_1R = r_1R + 1
                global r_2
                r_2 = r_2 +1
            
        dev_R.setDelegate( MyDelegate() )
        svc_R = dev_R.getServiceByUUID( 0xdfb0 )
        ch_R = svc_R.getCharacteristics()[0]
        val_R = ch_R.valHandle
        print(val_R)

        dev_R.writeCharacteristic(ch_R.valHandle+1, b"\x02\x00")
    
        while True:
            if (bt_power == 0):
                break
   
            if dev_R.waitForNotifications(1.0):
            # handleNotification() was called
                continue

            print("Waiting...")
        return
        
    def left():
        global dev_L
        dev_L.connect("F4:5E:AB:B1:14:FB")
        global bt_power

        class MyDelegate(btle.DefaultDelegate):
            def __init__(self):
                btle.DefaultDelegate.__init__(self)

            def handleNotification(self, cHandle, data):
                data = int(data)
                print("A notification was received from left:" + str(data))
                a = 1
                handle_data(a,data)
                global r_1L
                r_1L = r_1L +1
                
        dev_L.setDelegate( MyDelegate() )
        svc_L = dev_L.getServiceByUUID( 0xdfb0 )
        ch_L = svc_L.getCharacteristics()[0]
        val_L = ch_L.valHandle
        print(val_L)

        dev_L.writeCharacteristic(ch_L.valHandle+1, b"\x02\x00")
    
        while True:
            if (bt_power == 0):
                break
   
            if dev_L.waitForNotifications(1.0):
                # handleNotification() was called
                continue

            print("Waiting...")
        return
    
    if __name__ == '__main__':
        global p1
        p1 = Process(target = right)
        p1.start()
        global p2
        p2 = Process(target = left)
        p2.start()
    return
        

class start(FloatLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        #Window.size = (800 , 480)  #Sets window sixe to size of display
        #Window.fullscreen = True
        super(start, self).__init__(**kwargs)
        self.add_widget(
            AsyncImage(
                source="/home/pi/carbon.jpeg",
                size_hint= (1.5, 1.5),
                pos_hint={'center_x':.5, 'center_y':.5}))
        self.startbtn = Button(
                text="START",
                background_color=(0,1,0,1),
                size_hint=(.3, .3),
                pos_hint={'center_x': .5, 'center_y': .7})
        self.startbtn.bind(on_press=self.btn_pressedstart)
        self.add_widget(self.startbtn)

        self.quitbtn = Button(
                text="SAVE AND QUIT",
                background_color=(1,0,0,1),
                size_hint=(.2, .2),
                pos_hint={'center_x': .5, 'center_y': .3})
        self.quitbtn.bind(on_press=self.btn_pressedquit)
        self.add_widget(self.quitbtn)


        with self.canvas.before:
            Color(0, 0, 0, 0)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def btn_pressedstart(self, instance):
       self.remove_widget(self.startbtn)
       make_workbook()
       global wb
       global sheet1
       sheet1 = wb.add_worksheet('Power Phase')
       global sheet2
       sheet2 = wb.add_worksheet('Cadence')
       #Adds headers for different values
       sheet1.write(0, 0, 'Right Power')
       sheet1.write(0, 1, 'Right Crank Angle')
       sheet1.write(0, 2, 'Left Power')
       sheet1.write(0, 3, 'Left Crank Angle')
       sheet2.write(0, 0, 'Time')
       sheet2.write(0, 1, 'Average Cadence')
       
       print('Hello')
       data_processing()
       return
       
    def btn_pressedquit(self, instance):
        global wb
        wb.close()
        global bt_power
        bt_power = 0
        global p1
        p1.terminate()
        global p2
        p2.terminate()
        disconnect()
        print("Bye")
        self.add_widget(self.startbtn)
        MainApp.get_running_app().stop()
        Window.close()


class MainApp(App):

    def build(self):
        root = start()
        return root

if __name__ == '__main__':
    MainApp().run()
    
