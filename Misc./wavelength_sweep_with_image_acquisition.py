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


###########
# MAIN LOOP
###########
# loop emission over spectral range
peak_wavelengths = []  # Initialize the list to store peak wavelengths

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
    sleep(0.25)
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
    
    
    # Save the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = f'image_{iteration}.png'
    filepath = os.path.join(current_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', pad_inches=0)
    print(f'Image saved: {filepath}')
   
    # Show the plot
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