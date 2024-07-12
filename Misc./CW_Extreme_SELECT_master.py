from NKTP_DLL import *
from time import sleep
import numpy as np


COM_port = 'COM5'
#EXTREME_power_perc = 40

## WAVELENGTHS IN PM!!!! SEE SDK MANUAL

SELECT_output_perc = 100
## POWER is % INCREASE THAN ITS NORMAL (23%)!!!!

N_wavelengths = 15
Wavelength_min = 400000
Wavelength_max = 650000

Wavelengths = np.linspace(Wavelength_min,Wavelength_max, N_wavelengths) 




# openResult = openPorts(COM_port, 15, 0)
# print('Opening the comport EXTREME:', PortResultTypes(openResult))

# openResult = openPorts(COM_port, 16, 0)
# print('Opening the comport SELECT:', PortResultTypes(openResult))

# openResult = openPorts(COM_port, 18, 0)
# print('Opening the comport RF Driver:', PortResultTypes(openResult))

# COMMENT: somtimes need to reset interlock on restart

#rdResult, serial = deviceGetModuleSerialNumberStr(COM_port, 15)
#print('Serial EXTREME:', serial, DeviceResultTypes(rdResult))

rdResult, serial = deviceGetModuleSerialNumberStr(COM_port, 16)
print('Serial SELECT:', serial, DeviceResultTypes(rdResult))
      
# result = registerWriteU16(COM_port, 15, 0x31, 1, -1)
# print('Extreme power mode:', RegisterResultTypes(result))

# result = registerWriteU16(COM_port, 15, 0x37, 100, -1)
# print('Setting power level - Extreme:', RegisterResultTypes(result))


# result = registerWriteU16(COM_port, 15, 0x38, 100, -1)
# print('Setting current level - Extreme:', RegisterResultTypes(result))

# result = registerWriteU16(COM_port, 15, 0x30, 3, -1)
# print('Setting emission ON - Extreme:', RegisterResultTypes(result))


print('sleeping for 2 seconds...')
sleep(2.0)

result = registerWriteU16(COM_port, 18, 0x31, 1, -1)
print('XXX', RegisterResultTypes(result))

result = registerWriteU8(COM_port, 18, 0x75, 1, -1)
print('Crystal', RegisterResultTypes(result))




result = registerWriteU16(COM_port, 18, 0xB0, 100, -1)
print('Setting wavelength 1 perc', RegisterResultTypes(result))

#result = registerWriteU16(COM_port, 18, 0xC0, 100, -1)
#print('Setting wavelength 1 gain', RegisterResultTypes(result))

# result = registerWriteU8(COM_port, 18, 0x3C, 1, -1)
# print('Setting daughter', RegisterResultTypes(result))

    
for ii in range(N_wavelengths): 

    lam = Wavelengths[ii]
    lam = int(lam)
    
    # result = registerWriteU16(COM_port, 15, 0x37, 300 - ii*10, -1)
    # print('Setting power level - Extreme:', RegisterResultTypes(result))
    
    result = registerWriteU32(COM_port, 18, 0x90, lam, -1)
    print('Setting wavelength 1', RegisterResultTypes(result))
    
    result = registerWriteU8(COM_port, 18, 0x30, 1, -1)
    print('RF power ON', RegisterResultTypes(result))
    sleep(1)



result = registerWriteU8(COM_port, 18, 0x30, 0, -1)
print('RF power OFF', RegisterResultTypes(result))

print('sleeping for 3 seconds...')
sleep(3.0)


# result = registerWriteU8(COM_port, 15, 0x30, 0, -1)
# print('Setting emission OFF - Extreme:', RegisterResultTypes(result))


closeResult = closePorts(COM_port)
print('Close the comport:', PortResultTypes(closeResult))

### turn off

# result = registerWriteU8(COM_port, 16, 0x30, 0, -1)
# print('RF power OFF', RegisterResultTypes(result))

# result = registerWriteU8(COM_port, 15, 0x30, 1, -1)
# print('Setting emission OFF - Extreme:', RegisterResultTypes(result))