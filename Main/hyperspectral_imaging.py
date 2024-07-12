# -*- coding: utf-8 -*-
"""
@author: ojt210 - Owen Thomas
    This code creates a hypercube of specral data by shining a laser on a given object and performing a wavelength sweep, taking an image
    and a spectrometer reading for each iteration within the main loop.

    Before the main loop there are two calibration phases: a light-dark calibration for the spectrometer and a power normalisation stage 
    for the NKT Photonics SELECT AOTF. Without the power normalisation loop we would see a much larger discrepancy in the measured intensity 
    of each wavelength.

Light-Dark Calibration:
    
    As instructed, place the dark reference in front of the spectrometer, press enrter, and repeat for the light reference. Press enter 
    to move on to the power normalisation phase.

Initialise Variables and Power Normalisation:

    As prompted within the terminal determine the range of wavelengths over which you would like to perform the wavelength sweep, and the 
    number of steps you would like between the min and max values. You can thenm set the desired settings for the power normalisation calibration,
    by choosing the desired nuber of counts for each wavelength, the discrepancy tolerance and the maximum allowed number of iterations the loop
    may go through. After selecting your exposure time for the camera and the integration time for the spectrometer the code will then execute the
    power normalisation.
    
    Once the power normalisation loop has run, the calibration data is stored as a csv file to the same directory as the file is run from, and 
    called back later.

Main loop:

    Once calibrated, the system will immediately begin the main loop, performing a sweep across the prescribed range of wavelength values, for
    each iteration taking an image of the object and taking a spectral reading. This data is stored in a three dimensional hypercube, which is 
    visualised within the GUI described below.
    
GUI Construction:
    
    Once the main loop is coplete, a new window will appear to visualise the captured data. This window has the following capabilities:
        - A main window to view the image data, in grayscale, for each wavelength value
        - A slider below this window to scroll through the wavelength range and view how the image data changes
        - When a pixel is selected, a plot appears in the top right which demonstrates how the grayscale value of the selected pixel changes as 
          the wavelength varies.
        - In the bottom right we see an RGB reconstruction of the object.
        
Notes:
    
    If an error labeled "Device was physically removed", I belive this means the camera has overheated and turned itself off. In this case simply
    unplug and wait for camera to cool before running again.
    
    If the code is stopped mid loop,for example as above, devices may be left open which causes issues if the code is run again immediately after.
    The files:
    'laser_killswitch'
    'spec_killswitch'
    are helpful for getting round this.
    
    Communication with NKTP devices:
    
    To write to the register, we use the following syntax: result = registerWriteu8(a, b, c, d, e), where:
        - a = COM port where device is attached to desktop
        - b = device address
        - c = register
        - d = chosen value
        - e = -1
    See line 87 for an example of how to turn SuperK COMPACT emission ON. To understand this better, read the NKTP SDK instruction manual 
    located at C:\SDK 2. Page 52 describes the specific registers for the RF driver for SUperK SELECT.
"""
# Import relevant modules

import numpy as np
from NKTP_DLL import *
from time import sleep
import seabreeze.spectrometers as sb
from seabreeze.spectrometers import Spectrometer
import matplotlib.pyplot as plt
from pypylon import pylon
import pandas as pd
from scipy.interpolate import interp1d
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QDoubleSpinBox
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#################################################################################################################################################
# INITIALISE HARDWARE
#################################################################################################################################################

# Initialize COMPACT supercontinuum laser
COM_port = 'COM5'
result = registerWriteU8('COM4', 1, 0x30, 1, -1)
print('Emission: ON')

# Initialize spectrometer
spec = Spectrometer.from_serial_number("HR2B1032")
print(spec)

#################################################################################################################################################
# LIGHT-DARK CALIBRATION
#################################################################################################################################################

print("Place dark reference and press Enter")
input()
dark_reference = spec.intensities()

print("Place white reference and press Enter")
input()
white_reference = spec.intensities()

calibration_factors = (white_reference - dark_reference) / (max(white_reference) - min(dark_reference))

print("Calibration complete")
print(" ")

#################################################################################################################################################
# INITIALISE VARIABLES
#################################################################################################################################################

print("Initiate variables for wavelength sweep:")
Wavelength_min = int(input("Enter minimum wavelength (in pm): "))
Wavelength_max = int(input("Enter maximum wavelength (in pm): "))
N_wavelengths = int(input("Enter desired number of wavelength steps: "))

print(" ")

print("Initiate variables for power normalisation:")

TARGET_COUNT = int(input("Enter target counts: "))
TOLERANCE = int(input("Enter tolerance for discrepancy: "))
MAX_ITERATIONS = int(input("Enter maximum number of iterations: "))

print(" ")

print("Set camera and spectrometer settings:")

print(" ")

exposure_time = float(input("Enter desired camera exposure time (in microseconds): "))
spec_integration_time = int(input("Enter desired spectrometer integration time (in microseconds): "))

Wavelengths = np.linspace(Wavelength_min, Wavelength_max, N_wavelengths)
spec.integration_time_micros(spec_integration_time)

print("New settings:")
print(f"Wavelength range: {Wavelength_min} pm to {Wavelength_max} pm")
print(f"Number of wavelength steps: {N_wavelengths}")
print(f"Camera exposure time: {exposure_time} microseconds")
print(f"Spectrometer integration time: {spec_integration_time} microseconds")

print("Press ENTER to begin power normalization")
input()

final_amplitudes = np.zeros(N_wavelengths)
final_counts = np.zeros(N_wavelengths)

# Perform light-dark calibration on spectrometer reading
def get_spectrometer_count(wavelength):
    spec.integration_time_micros(spec_integration_time)
    intensities = spec.intensities()
    wavelengths = spec.wavelengths()
    index = np.argmin(np.abs(wavelengths - wavelength/1000))
    calibrated_intensity = (intensities[index] - dark_reference[index]) / calibration_factors[index]
    return calibrated_intensity

# Initialize camera
tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice())

# Get image size to set hypercube dimensions
camera.Open()
camera.ExposureTime.SetValue(exposure_time)
camera.StartGrabbing(1)
grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)
if grab.GrabSucceeded():
    img = grab.GetArray()
    height, width = img.shape
camera.Close()

#################################################################################################################################################
# POWER NORMALISATION LOOP
#################################################################################################################################################

for i, wavelength in enumerate(Wavelengths):
    lam = int(wavelength)
    amplitude = 500
    
    for iteration in range(MAX_ITERATIONS):
        result = registerWriteU32(COM_port, 25, 0x90, lam, -1)
        print(f'Setting wavelength {lam} pm')
        
        amplitude = int(amplitude)
        result = registerWriteU16(COM_port, 25, 0xB0, amplitude, -1)
        print(f'Setting amplitude {amplitude}')
        
        result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
        print('RF power ON')
        
        sleep(0.1)
        
        count = get_spectrometer_count(wavelength)
        print(f'Count: {count}')
        
        if abs(count - TARGET_COUNT) <= TOLERANCE:
            print(f'Target reached for wavelength {lam} pm')
            break
        
        error = TARGET_COUNT - count
        step_size = max(1, min(100, abs(int(error / 3))))
        
        if count < TARGET_COUNT:
            amplitude = min(1000, amplitude + step_size)
        else:
            amplitude = max(1, amplitude - step_size)
        
        result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
        print('RF power OFF')
        
        if iteration == MAX_ITERATIONS - 1:
            print(f'Warning: Max iterations reached for wavelength {lam} pm')
    
    final_amplitudes[i] = amplitude
    final_counts[i] = count

# Save calibration results
np.savetxt('calibration_results.csv', 
           np.column_stack((Wavelengths, final_amplitudes, final_counts)), 
           delimiter=',', 
           header='Wavelength (pm),Amplitude,Count',
           comments='')

print("Calibration and power normalization complete. Results saved to 'calibration_results.csv'")

# Load calibration data for wavelength sweep
calibration_data = pd.read_csv('calibration_results.csv')
wavelengths_cal = calibration_data['Wavelength (pm)'].values
amplitudes_cal = calibration_data['Amplitude'].values

# Create interpolation function
amplitude_interpolator = interp1d(wavelengths_cal, amplitudes_cal, kind='linear', fill_value='extrapolate')

#################################################################################################################################################
# INITIALISE LISTS AND FINAL VARIABLE CHANGES
#################################################################################################################################################

peak_wavelengths = []
total_intensities = None

# Initialize hypercube (3-d array, and NxMxL matrix where N and M are the image dimensions, L is the wavelength range and 
# the elements store grayscale values)
hypercube = np.zeros((height, width, N_wavelengths), dtype=np.uint16)

# Power compensation function
def calculate_power_compensation(wavelength):
    wavelength_nm = wavelength / 1000
    calibrated_amplitude = amplitude_interpolator(wavelength)
    normalized_amplitude = calibrated_amplitude / 1000
    compensation_factor = 1 / normalized_amplitude if normalized_amplitude > 0 else 1
    return compensation_factor

def apply_power_compensation(wavelengths, intensities):
    compensated_intensities = np.zeros_like(intensities)
    for i, (wavelength, intensity) in enumerate(zip(wavelengths, intensities)):
        compensation_factor = calculate_power_compensation(wavelength)
        compensated_intensities[i] = intensity / compensation_factor
    return compensated_intensities

#################################################################################################################################################
# MAIN LOOP - WAVELENGTH SWEEP
#################################################################################################################################################

for i in range(N_wavelengths):
    iteration = i + 1
    lam = int(Wavelengths[i])
    
    power_factor = calculate_power_compensation(lam)
    
    result = registerWriteU32(COM_port, 25, 0x90, lam, -1)
    print('Setting wavelength', i + 1, RegisterResultTypes(result))
    
    amplitude = int(1000 / power_factor)
    amplitude = max(1, min(1000, amplitude))
    result = registerWriteU16(COM_port, 25, 0xB0, amplitude, -1)
    print('Setting amplitude', amplitude, RegisterResultTypes(result))
    
    result = registerWriteU8(COM_port, 25, 0x30, 1, -1)
    print('RF power ON', RegisterResultTypes(result))
    
    sleep(0.05)

    spec.integration_time_micros(spec_integration_time)
    wavelengths = spec.wavelengths()
    intensities = spec.intensities()
    normalized_intensities = intensities - dark_reference

    if total_intensities is None:
        total_intensities = np.zeros_like(normalized_intensities)

    total_intensities += normalized_intensities
    
    camera.Open()
    camera.ExposureTime.SetValue(exposure_time)
    camera.StartGrabbing(1)
    grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_Return)
    
    if grab.GrabSucceeded():
        img = grab.GetArray()
        print(f'Size of image: {img.shape}')
        hypercube[:, :, i] = img

    camera.Close()
    print('Camera: Closed')
    
    # plot the cumulative intensity of each wavelength value for each iteration
    plt.plot(wavelengths, total_intensities)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Cumulative Normalized Intensity')
    plt.title(f'Cumulative Normalized Spectrum up to Iteration {iteration}')
    plt.xlim(Wavelength_min/1000, Wavelength_max/1000)
    plt.show()

compensated_intensities = apply_power_compensation(wavelengths, total_intensities)

# Plot the final cumulative intensity of each wavelength value
plt.plot(wavelengths, total_intensities)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Cumulative Normalized Intensity')
plt.title(f'Cumulative Normalized Spectrum - All Iterations')
plt.xlim(Wavelength_min/1000, Wavelength_max/1000)
plt.show()

# Clean up and close devices

result = registerWriteU8(COM_port, 25, 0x30, 0, -1)
print('RF power: OFF')

result = registerWriteU8('COM4', 1, 0x30, 0, -1)
print('Emission: OFF')

camera.Close()
print('Camera: Closed')

spec.close()
print('Spectrometer: CLOSED')

closeResult = closePorts(COM_port)
print('Closing COM ports')

#################################################################################################################################################
# GUI CONSTRUCTION
#################################################################################################################################################

class HyperspectralViewer(QMainWindow):
    def __init__(self, hypercube, wavelengths):
        super().__init__()
        self.hypercube = hypercube
        self.wavelengths = wavelengths
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.delayed_update)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hyperspectral Image Viewer')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        self.hyper_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.hyper_ax = self.hyper_canvas.figure.subplots()
        left_layout.addWidget(self.hyper_canvas)
        
        slider_layout = QHBoxLayout()

        self.wavelength_slider = QSlider(Qt.Horizontal)
        self.wavelength_slider.setMinimum(0)
        self.wavelength_slider.setMaximum(1000)
        self.wavelength_slider.valueChanged.connect(self.slider_changed)
        slider_layout.addWidget(self.wavelength_slider)
        
        self.wavelength_spinbox = QDoubleSpinBox()
        self.wavelength_spinbox.setRange(min(self.wavelengths), max(self.wavelengths))
        self.wavelength_spinbox.setSingleStep(0.1)
        self.wavelength_spinbox.valueChanged.connect(self.spinbox_changed)
        slider_layout.addWidget(self.wavelength_spinbox)
        
        left_layout.addLayout(slider_layout)

        layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        self.spectrum_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.spectrum_ax = self.spectrum_canvas.figure.subplots()
        right_layout.addWidget(self.spectrum_canvas)

        self.rgb_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.rgb_ax = self.rgb_canvas.figure.subplots()
        right_layout.addWidget(self.rgb_canvas)

        layout.addLayout(right_layout)

        self.update_hyper_image(0)
        self.generate_rgb_image()
        self.hyper_canvas.mpl_connect('button_press_event', self.on_click)

    def slider_changed(self, value):
        wavelength = self.map_slider_to_wavelength(value)
        self.wavelength_spinbox.setValue(wavelength)
        self.update_timer.start(50)

    def spinbox_changed(self, value):
        slider_value = self.map_wavelength_to_slider(value)
        self.wavelength_slider.setValue(slider_value)
        self.update_timer.start(50)

    def delayed_update(self):
        wavelength = self.wavelength_spinbox.value()
        wavelength_index = self.find_nearest_wavelength_index(wavelength)
        self.update_hyper_image(wavelength_index)

    def map_slider_to_wavelength(self, slider_value):
        return min(self.wavelengths) + (slider_value / 1000) * (max(self.wavelengths) - min(self.wavelengths))

    def map_wavelength_to_slider(self, wavelength):
        return int(1000 * (wavelength - min(self.wavelengths)) / (max(self.wavelengths) - min(self.wavelengths)))

    def find_nearest_wavelength_index(self, wavelength):
        return np.argmin(np.abs(self.wavelengths - wavelength))

    def update_hyper_image(self, wavelength_index):
        self.hyper_ax.clear()
        self.hyper_ax.imshow(self.hypercube[:, :, wavelength_index], cmap='gray', vmin = 0, vmax = 255)
        self.hyper_ax.set_title(f'Wavelength: {self.wavelengths[wavelength_index]:.2f} nm')
        self.hyper_canvas.draw()

    def generate_rgb_image(self):
        r = self.hypercube[:, :, -1]
        g = self.hypercube[:, :, len(self.wavelengths)//2]
        b = self.hypercube[:, :, 0]
        rgb = np.stack([r, g, b], axis=-1)
        rgb = rgb / np.max(rgb)
        self.rgb_ax.imshow(rgb)
        self.rgb_ax.set_title('RGB Representation')
        self.rgb_canvas.draw()

    def update_spectrum(self, row, col):
        spectrum = self.hypercube[row, col, :]
        self.spectrum_ax.clear()
        self.spectrum_ax.plot(self.wavelengths, spectrum)
        self.spectrum_ax.set_xlabel('Wavelength (nm)')
        self.spectrum_ax.set_ylabel('Intensity')
        self.spectrum_ax.set_title(f'Spectrum at ({row}, {col})')
        self.spectrum_ax.tick_params(axis='x', rotation=45)
        self.spectrum_canvas.figure.tight_layout()
        self.spectrum_canvas.draw()

    def on_click(self, event):
        if event.inaxes == self.hyper_ax:
            col, row = int(event.xdata), int(event.ydata)
            self.update_spectrum(row, col)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = HyperspectralViewer(hypercube, Wavelengths)
    viewer.show()
    sys.exit(app.exec_())