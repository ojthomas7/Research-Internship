# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 11:37:06 2024

@author: ojt210
"""
####################
# INITIALISE COMPACT
####################

from NKTP_DLL import *
from time import sleep
import numpy as np

COM_port = 'COM5'

# turn COMPACT emission on
result = registerWriteU8('COM4', 1, 0x30, 1, -1)
print('Emission: ON')

#######################
# INITIALISE VARIABLES
#######################

# initiate desired wavelength (in picometres)
wavelength = 600000

# select exposure time
exposure_time = 74920.0

###################
# INITIALISE CAMERA
###################

from pypylon import pylon
import numpy as np
import matplotlib.pyplot as plt


tl_factory = pylon.TlFactory.GetInstance()
devices = tl_factory.EnumerateDevices()
for device in devices:
    print(device.GetFriendlyName())
    

tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice())

# open camera
camera.Open()
print('Camera: OPEN')

##############################
# RF EMISSION AND TAKE READING
##############################

on_time = 1.0

result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
print('RF power ON', RegisterResultTypes(result))

print('laser emission')
sleep(on_time)


camera.ExposureTime.SetValue(exposure_time)
camera.StartGrabbing(1)
grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)
if grab.GrabSucceeded():
    img = grab.GetArray()
    print(f'Size of image: {img.shape}')
camera.Close()

plt.imshow(img, cmap='gray')
plt.title('Captured Image')
plt.axis('off')
plt.show()

# turn off RF power
result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
print('RF power: OFF')

# turn COMPACT emission off
result = registerWriteU8('COM4', 1, 0x30, 0, -1)
print('Emission: OFF')

# close camera
camera.Close()
print('Camera: Closed')