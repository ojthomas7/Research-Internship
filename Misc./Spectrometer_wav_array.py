# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 12:19:00 2024

@author: ojt210
"""


import numpy as np
import scipy as sp
from scipy.signal import find_peaks


# open spectrometer
import seabreeze.spectrometers as sb
from seabreeze.spectrometers import list_devices, Spectrometer
devices = list_devices()
print(devices)


# acquire spectrum
spec = Spectrometer.from_serial_number('HR2B1032')
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

# close spectrometer
spec.close()