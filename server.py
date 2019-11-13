#!/usr/bin/env python3
import time
import struct
from neopixel import *
import argparse
from bluetooth import *
from threading import Thread

ColorList = []
AnimationList = []
AnimationInProgress = False

for i in range(64):
    ColorList.append(0)

def isHeaderFrame(data):
    if int.from_bytes(data[0:4], byteorder='little') == 0xFFFFFFFF:
        return True
    else:
        return False

def displayAnimation(AnimationList, strip):
    global AnimationInProgress
    AnimationInProgress=True
    while AnimationInProgress == True:
        for matrix in AnimationList:
            setLeds(matrix, strip)
            time.sleep(1)

def setLeds(data, strip):
    for x in range(64):
        value = int.from_bytes(data[x*4:x*4+4], byteorder='little')
        if value != ColorList[x]:
            strip.setPixelColor(x, value)
            print("x: %d value: %d" % (x, value))
            strip.show()
            ColorList[x] = value

def waitForData(server_sock, strip, ReceivingAnimation):
    global AnimationInProgress
    global AnimationList
    try:
        while True:
            client_sock, client_info = server_sock.accept()
            print("Accepted connection from ", client_info)
            print("waiting for data")
            data = client_sock.recv(256)
            if len(data) != 256:
                pass
            else:
                if AnimationInProgress == True:
                    AnimationInProgress = False
                if isHeaderFrame(data):
                    if ReceivingAnimation == False:
                        ReceivingAnimation = True
                    else:
                        ReceivingAnimation = False
                        thread = Thread(target = displayAnimation, args = (AnimationList,strip,))
                        thread.start()
                        #displayAnimation(AnimationList)
                else:
                    if ReceivingAnimation == False:
                        setLeds(data, strip)
                    else:
                        AnimationList.append(data)
    except IOError:
        print("connection closed")
        client_sock.close()
        waitForData(server_sock, strip, ReceivingAnimation)
        pass
    

hdmi_force_hotplug=1
hdmi_force_edid_audio=1

# LED strip configuration:
LED_COUNT      = 64      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 20     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "LtLServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)


strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()
AnimationInProgress = False
waitForData(server_sock, strip, False)

print("disconnected")

server_sock.close()
print("all done")
