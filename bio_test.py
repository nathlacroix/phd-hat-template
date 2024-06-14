# This test file is to test the LCD screen and button functionalities.
# run this script to verify that all components work correctly.
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw
import adafruit_ssd1306
from src.sola_board_game.bio import *
import time
import neopixel

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)


# Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP


# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
# test something
width = disp.width
height = disp.height

# test_plot = FreqPlot(width, height, buffer=16, nb_pts=3)
# test_plot.update_freq_plot()
# disp.image(test_plot.main_img)
# disp.show()
print('width = %d' % width)
print('height = %d' % height)

freq_plot = FreqPlot(w=width, h=height, buffer=16, nb_pts=3)
noise_plot = NoisePlot(w=width, h=height, buffer=16, nb_pts=28)
disp.image(freq_plot.main_img)
disp.show()

led_indices = {
    "q3":  0,
    "dark": 1,
    "q1":  2,
    "bright":  3,
    "q2":  4,
}

PI_PIN_NEOPIXELS = board.D21
NEOPIXEL_COUNT = 5
pixels = neopixel.NeoPixel(
    PI_PIN_NEOPIXELS,
    NEOPIXEL_COUNT,
    brightness=0.2,
    # auto_write=False,
    pixel_order=neopixel.GRBW,
)

def light_up_pixel(index, color):
	print(f"Lighting up pixel {index} with color {color}.")
	pixels[index] = color
	pixels.show()
	time.sleep(0.1)  # Add a delay to see the change

# Map frequency to color for both qubits
# Light up bright and dark states when qubits are in resonance
# Light up dark once the noise profile is near the cost function (also do the mapping)?


while True:
	if not button_R.value:
		freq_plot.update_marker(1)

	if not button_L.value:
		freq_plot.update_marker(-1)

	if not button_U.value:
		freq_plot.update_value(-0.1)
		for idx, freq in enumerate(freq_plot.values):
			rgb = value_to_rgb(freq)+(0,)
			light_up_pixel(idx, rgb)

	if not button_D.value:
		freq_plot.update_value(0.1)
		for idx, freq in enumerate(freq_plot.values):
			rgb = value_to_rgb(freq)+(0,)
			light_up_pixel(idx, rgb)

	if (freq_plot.values[0] == freq_plot.values[1]) and (freq_plot.values[2] == (freq_plot.values[1] + freq_plot.hybridization)):
		print('First game done!')
		success_img = Image.new('1', (width, height))
		success_draw = ImageDraw.Draw(success_img)
		success_draw.text((16, 32), 'First game done! :)', fill=1)
		disp.image(success_img)
		disp.show()
		time.sleep(5)
		break
	else:
		print(freq_plot.values, freq_plot.hybridization)

	disp.image(freq_plot.main_img)
	disp.show()

disp.image(noise_plot.main_img)
disp.show()

while True:
	if not button_R.value:
		noise_plot.update_marker(1)

	if not button_L.value:
		noise_plot.update_marker(-1)

	if not button_U.value:
		noise_plot.update_value(-0.1)

	if not button_D.value:
		noise_plot.update_value(0.1)

	disp.image(noise_plot.main_img)
	disp.show()
