# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 12:41:35 2024

@author: ojt210

This file initialises the hardware components (SuperK COMPACT and Oceanview
Spectrometer serial: HR2B1032) and allows user to set desires wavelength (in 
PICOMETRES) of laser emission from COMPACT/ AOTF. Laser emission occurs for 5.0
seconds in which time the spectrometer takes a reading, finds the index of the 
wavelength with the greatest intensity and returns this wavelength in nanometres.

This is imperfect: this code does not seeem to work for lower frquencies, returning
a value correspomnding to background noise. There is also discrepancy betweeen
the expected wavelength value and the returned value, likely due to background
noise, response functions of each piece of hardware and lack accounting for this
response function. This response function results in varying output power
for different wavelengths. This can be improved by enhancing our physical setup but will 
inevitably require a correcting curve for optimal accuracy.

"""

####################
# INITIALISE COMPACT
####################

from NKTP_DLL import *
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

COM_port = 'COM5'

# initiate desired wavelength (in picometres)
wavelength1 = 600000
wavelength2 = 500000

# determine length of time for laser emission (seconds)
on_time = 5.0 

# turn COMPACT emission on
result = registerWriteU8('COM4', 1, 0x30, 1, -1)
print('Emission: ON')

# set COMPACT to emit at given wavelength
result = registerWriteU32(COM_port, 25, 0x90, wavelength1, -1)
result = registerWriteU32(COM_port, 25, 0x90, wavelength2, -1)
print('Setting wavelength:', wavelength1, 'pm', RegisterResultTypes(result))

#########################
# INITIALISE SPECTROMETER
#########################

import numpy as np
import seabreeze.spectrometers as sb
from seabreeze.spectrometers import Spectrometer
spec = Spectrometer.from_serial_number("HR2B1032")
print(spec)

##############################
# RF EMISSION AND TAKE READING
##############################

on_time = 2.0

result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
print('RF power ON', RegisterResultTypes(result))

print('laser emission')
sleep(on_time)


# acquire spectrum
spec.integration_time_micros(100000)

# Get wavelengths and intensities
wavelengths = spec.wavelengths()
intensities = spec.intensities()


# find index of maximum intensity to locate spectral peak
max_intensity_index = np.argmax(intensities)

# print the index of the most intense wavelength
print(max_intensity_index)

# print wavelength of spectral peak
print(wavelengths[max_intensity_index])

plt.plot(wavelengths, intensities)
plt.show()

# turn COMPACT emission off
result = registerWriteU8('COM4', 1, 0x30, 0, -1)
print('Emission: OFF')

# turn off RF power
result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
print('RF power: OFF')

# close spectrometer
spec.close()
print('Sec: CLOSED')

# close COM ports
closeResult = closePorts(COM_port)
print('Closing COM ports')