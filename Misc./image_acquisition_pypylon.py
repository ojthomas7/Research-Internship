# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:57:58 2024

@author: ojt210
"""

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
    
camera.Open()
camera.ExposureTime.SetValue(74920.0)
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
