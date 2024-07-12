# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:45:21 2024

@author: ojt210

modified swep_image_spectrometer.py to subtract backgound noise from the spectrometers reading.
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

#########################
# INITIALISE SPECTROMETER
#########################

import numpy as np
import seabreeze.spectrometers as sb
from seabreeze.spectrometers import Spectrometer
spec = Spectrometer.from_serial_number("HR2B1032")
print(spec)

######################
# INITIALISE VARIABLES
######################

# create desired wavelength range
N_wavelengths = 20
Wavelength_min = 500000
Wavelength_max = 650000
    
Wavelengths = np.linspace(Wavelength_min,Wavelength_max, N_wavelengths)

# select exposure time
exposure_time = 74920.0

#############################################
# NORMALIZE SPECTROMETER FOR BACKGROUND NOISE
#############################################

# Measure background before the main loop
spec.integration_time_micros(10000)
background = spec.intensities()

#########################################################################
# MAIN LOOP
#########################################################################
# loop emission over spectral range
peak_wavelengths = []  # Initialize the list to store peak wavelengths
total_intensities = None

for i in range(N_wavelengths):
    iteration = i + 1
    
    # open camera
    camera.Open()
    print('Camera: OPEN')
    lam = Wavelengths[i]
    lam = int(lam)
    result = registerWriteU32(COM_port, 25, 0x90, lam, -1)
    print('Setting wavelength', i + 1, RegisterResultTypes(result))
    result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
    print('RF power ON', RegisterResultTypes(result))
    sleep(0.05)

    # acquire spectrum
    spec.integration_time_micros(10000)

    # Get wavelengths and intensities
    wavelengths = spec.wavelengths()
    intensities = spec.intensities()

    # Subtract background noise
    normalized_intensities = intensities - background

    # Use normalized_intensities for further calculations
    if total_intensities is None:
        total_intensities = np.zeros_like(normalized_intensities)

    # Add current normalized intensities to the cumulative sum
    total_intensities += normalized_intensities

    # find index of maximum intensity to locate spectral peak
    max_intensity_index = np.argmax(normalized_intensities)

    # print the index of the most intense wavelength
    print(max_intensity_index)

    # print wavelength of spectral peak
    peak_wavelength = wavelengths[max_intensity_index]
    print(peak_wavelength)

    # Store the peak wavelength in the list
    peak_wavelengths.append(peak_wavelength)
    
    camera.ExposureTime.SetValue(exposure_time)
    camera.StartGrabbing(1)
    grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)
    if grab.GrabSucceeded():
        img = grab.GetArray()
        print(f'Size of image: {img.shape}')

    # close camera
    camera.Close()
    print('Camera: Closed')
    plt.imshow(img, cmap='gray')
    plt.title(f'Iteration {iteration}, wavelength {Wavelengths[i]} pm')
    plt.axis('off')
    # save image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = f'image_{iteration}_wavelength_{lam / 1000}_nm.png'
    filepath = os.path.join(current_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', pad_inches=0)
    print(f'Image saved: {filepath}')
    plt.show()
    
    plt.plot(wavelengths, total_intensities)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Cumulative Normalized Intensity')
    plt.title(f'Cumulative Normalized Spectrum up to Iteration {iteration}')
    plt.xlim(Wavelength_min/1000, Wavelength_max/1000)
    plt.show()


plt.plot(wavelengths, total_intensities)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Cumulative Normalized Intensity')
plt.title(f'Cumulative Normalized Spectrum - All Iterations')
plt.xlim(Wavelength_min/1000, Wavelength_max/1000)
plt.show()

#current_dir = os.path.dirname(os.path.abspath(__file__))
#filename = cumulative_spec.png
#filepath = os.path.join(current_dir, filename)
#plt.savefig(filepath, bbox_inches='tight', pad_inches=0)
#print(f'Image saved: {filepath}')


# turn off RF power
result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
print('RF power: OFF')

# turn COMPACT emission off
result = registerWriteU8('COM4', 1, 0x30, 0, -1)
print('Emission: OFF')

# close camera
camera.Close()
print('Camera: Closed')

# close spectrometer
spec.close()
print('Sec: CLOSED')

# close COM ports
closeResult = closePorts(COM_port)
print('Closing COM ports')