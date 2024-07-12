"""
Created: 19/06/2024
Test code reproducing example code sent by Dr Calum Williams.
This script imports the relevant modules, turns on laser emission, emits a
range of spectra and then turns off RF laser emission.

"""

from NKTP_DLL import *
from time import sleep
import numpy as np

COM_port = 'COM5'

# create desired wavelength range
N_wavelengths = 20
Wavelength_min = 400000
Wavelength_max = 650000
    
Wavelengths = np.linspace(Wavelength_min,Wavelength_max, N_wavelengths)

# turn COMPACT emission on
result = registerWriteU8('COM4', 1, 0x30, 1, -1)
print('Emission: ON')

sleep(2.0)

# loop emission over spectral range
for i in range(N_wavelengths):
    
    lam = Wavelengths[i]
    lam = int(lam)
    result = registerWriteU32(COM_port, 25, 0x90, lam, -1)
    print('Setting wavelength', i, RegisterResultTypes(result))
    result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
    print('RF power ON', RegisterResultTypes(result))
    sleep(0.25)
    

# turn COMPACT emission off
result = registerWriteU8('COM4', 1, 0x30, 0, -1)
print('Emission: OFF')


# turn off RF power
result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
print('RF power OFF', RegisterResultTypes(result))

sleep(2.0)

# Close COM ports
closeResult = closePorts(COM_port)
print('Closing COM ports', PortResultTypes(closeResult))

