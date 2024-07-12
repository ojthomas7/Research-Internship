# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:21:32 2024

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

#########################
# INITIALISE SPECTROMETER
#########################

import numpy as np
import seabreeze.spectrometers as sb
from seabreeze.spectrometers import Spectrometer
spec = Spectrometer.from_serial_number("HR2B1032")
print(spec)

########################
# INITIALISE WAVELENGTHS
########################

# create desired wavelength range
N_wavelengths = 20
Wavelength_min = 500000
Wavelength_max = 650000
    
Wavelengths = np.linspace(Wavelength_min,Wavelength_max, N_wavelengths)

##################################################################
# MAIN LOOP
##################################################################
# loop emission over spectral range
peak_wavelengths = []  # Initialize the list to store peak wavelengths

for i in range(N_wavelengths):
    
    lam = Wavelengths[i]
    lam = int(lam)
    result = registerWriteU32(COM_port, 25, 0x90, lam, -1)
    print('Setting wavelength', i + 1, RegisterResultTypes(result))
    result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
    print('RF power ON', RegisterResultTypes(result))
    sleep(0.25)
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
    peak_wavelength = wavelengths[max_intensity_index]
    print(peak_wavelength)

    # Store the peak wavelength in the list
    peak_wavelengths.append(peak_wavelength)

print(peak_wavelengths)
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