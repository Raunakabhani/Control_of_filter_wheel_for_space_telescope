import serial
import time
from ctypes import *
import kivy
import math
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
kivy.require('2.1.0')

# EPOS Command Library path
path='.\\EposCmd64.dll' 

# Load library
cdll.LoadLibrary(path)
epos = CDLL(path)

# Defining return variables from Library Functions
ret = 0
pErrorCode = c_uint()
pDeviceErrorCode = c_uint()
nodeID = 1  #from epos studio 
baudrate = 1000000 #fixed
timeout = 500   #fixed


acceleration =4
deceleration =4

#initialization
keyHandle = epos.VCS_OpenDevice(b'EPOS4', b'MAXON SERIAL V2', b'USB', b'USB0', byref(pErrorCode)) # specify EPOS version and interface (interface from epos studio)

epos.VCS_SetProtocolStackSettings(keyHandle, baudrate, timeout, byref(pErrorCode)) # set baudrate
epos.VCS_ClearFault(keyHandle, nodeID, byref(pErrorCode)) # clear all faults
epos.VCS_ActivateProfilePositionMode(keyHandle, nodeID, byref(pErrorCode)) # activate profile position mode
epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode)) # enable device

# closed loop feedback of motor position
def GetPositionIs():
    global pPositionIs
    pPositionIs=c_long()
    pErrorCode=c_uint()
    ret=epos.VCS_GetPositionIs(keyHandle, nodeID, byref(pPositionIs), byref(pErrorCode))
    global actual_filter
    return pPositionIs.value # motor steps

GetPositionIs()


#Move to position at specified speed(rpm)
def MoveToPositionSpeed(target_position_input,target_speed):
    while True:
        actual_value=GetPositionIs()
        print('Motor position: %s' % (actual_value)) # to print motor position continuously
        epos.VCS_SetPositionProfile(keyHandle, nodeID, target_speed, acceleration, deceleration, byref(pErrorCode)) # set profile parameters
        epos.VCS_MoveToPosition(keyHandle, nodeID, target_position_input,False,False, byref(pErrorCode)) # move to position
        time.sleep(1)
        if  (target_position_input-20)<target_position_input<(target_position_input+20):
            #print("i am here")
            time.sleep(0.5)
            break

# set the window size
#Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'height', '650')
Config.set('graphics', 'weidth', '650')


# load the kivy language file
Builder.load_string('''
    
<CircleButton>:
    size_hint: (.5, .5)
    size:100, 100 #dia of circular buttton
    background_color: (0,0, 0, 0)
    canvas.before:
        Color:
            rgba: (0.9,0.41,0.07,1)
        Line:
            width: 1.5 #thickness of circle    
            circle:
                (self.center_x, self.center_y, min(self.width, self.height)/2, 0, 500, 500)
''')


class CircleButton(Button):
    def __init__(self, **kwargs):
        super(CircleButton, self).__init__(**kwargs)
        self.color = [0.23, 0.65, 0.94, 1] #color of text inside circle

# class in which we are creating the canvas
class CanvasWidget(Widget):
    def __init__(self, **kwargs):
        super(CanvasWidget, self).__init__(**kwargs)
 
        # Arranging Canva
        with self.canvas:
            Color(0,0, 0.1, 1)  # set the colour #rgb
            self.rect = Rectangle(source ='download.jpg',
                                  pos = self.pos, size = self.size)
            # Update the canvas as the screen size change
            # if not use this next 5 line the
            # code will run but not cover the full screen
            self.bind(pos = self.update_rect,
                  size = self.update_rect)
            #circular button
            super(CanvasWidget, self).__init__(**kwargs)
            self.radius = 200
            self.center_x = 0  #centre of all scene
            self.center_y = 0
            self.buttons = []
            for i in range(7):
                angle = i * ((360 / 7))

                #ACTUAL BUTTON
                button2 = Button(text=f'Filter {i+1}',size=(100,100),size_hint=(0.5,0.5),background_normal='button_circle.png')
                button2.center_x = self.center_x + (self.radius) * math.cos(math.radians(angle)) +770  #BUTTON CENTRE
                button2.center_y = self.center_y + (self.radius) * math.sin(math.radians(angle)) +400
                button2.bind(on_press=lambda btn, i=i: self.on_button_pressed(i))
                self.buttons.append(button2)
                self.add_widget(button2)

    def on_button_pressed(self,i):
        global desired_filter
        desired_filter= i+1
        print(f"Desired Filter here is {desired_filter}")


        if -1000<GetPositionIs()<1000:
            actual_filter=1
            print(f"ctual_filter here is {actual_filter}")
            #print("this is filter one")

        elif 17700<GetPositionIs()<19700:
            actual_filter=2
            print(f"actual_filter here is {actual_filter}")
            #print("this is filter two")

        elif 36500<GetPositionIs()<38500:
            actual_filter=3
            print(f"actual_filter here is {actual_filter}")
            #print("this is filter three")

        elif 55500<GetPositionIs()<57500:
            actual_filter=4
            print(f"actual_filter here is {actual_filter}")
            #print("this is filter four")

        elif 74100<GetPositionIs()<76100:
            actual_filter=5
            print(f"actual_filter here is {actual_filter}")
            #print("this is filter five")

        elif 92800<GetPositionIs()<94800:
            actual_filter=6
            print(f"actual_filter here is {actual_filter}")
            #print("this is filter six")

        elif 111500<GetPositionIs()<113500:
            actual_filter=7
            print(f"actual_filter here is {actual_filter}")


#positive desire-actual
        if (desired_filter-actual_filter)==1:
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==2: 
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
        elif (desired_filter-actual_filter)==3: 
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==4: 
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==5: 
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==6: 
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))


        elif (desired_filter-actual_filter)==7: 
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))


#negative desired - actual
        elif (desired_filter-actual_filter)==-1:
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
        elif (desired_filter-actual_filter)==-2: 
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
        elif (desired_filter-actual_filter)==-3:  
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==-4: 
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==-5: 
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==-6: 
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))

        elif (desired_filter-actual_filter)==-7: 
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))
            MoveToPositionSpeed(-6200,4)
            epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode))
            time.sleep(1)
            epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode))


        return desired_filter

    def movement(self,desired_filter):
        if desired_filter==1:
            MoveToPositionSpeed(12400,100)


    # update function which makes the canvas adjustable.
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
        #ISRO IMAGE
        self.img = Image(source ='ISRO_Logo.png')
        self.img.allow_stretch = True
        self.img.keep_ratio = True
        self.img.size_hint_x = 1
        self.img.size_hint_y = 1
        self.img.opacity =1
        self.img.pos = (20, 670)

        #SAC IMAGE
        self.img2= Image(source ='SAC2.png')
        self.img2.allow_stretch = True
        self.img2.keep_ratio = True
        self.img2.size_hint_x = 10
        self.img2.size_hint_y = 10
        self.img2.opacity = 1
        self.img2.pos=(1400,670)
        s = Widget()
        s.add_widget(self.img)
        #return s

# Create the App Class
class Filter_Wheel(App):
    def build(self):
        return CanvasWidget() 

        
# run the App
Filter_Wheel().run()




