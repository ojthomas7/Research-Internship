from NKTP_DLL import *
from time import sleep
import numpy as np

COM_port = 'COM5'

# initiate desired wavelength (in picometres)
wavelength = 600000

# determine length of time for laser emission (seconds)
on_time = 10.0 

# turn COMPACT emission on
result = registerWriteU8('COM4', 1, 0x30, 1, -1)
print('Emission: ON')

# set COMPACT to emit at given wavelength
result = registerWriteU32(COM_port, 25, 0x90, wavelength, -1)
print('Setting wavelength:', wavelength, 'pm', RegisterResultTypes(result))


result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
print('RF power ON', RegisterResultTypes(result))

print('laser emission')
sleep(on_time)


# turn COMPACT emission off
result = registerWriteU8('COM4', 1, 0x30, 0, -1)
print('Emission: OFF')

# turn off RF power
result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
print('RF power: OFF')

# close COM ports
closeResult = closePorts(COM_port)
print('Closing COM ports')