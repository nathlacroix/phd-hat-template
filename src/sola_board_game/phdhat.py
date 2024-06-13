from pathlib import Path
import random
import time

import adafruit_ssd1306
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import numpy as np
from PIL import ImageFont, ImageDraw, Image



PI_PIN_SOLA_3DI = board.D13
PI_PIN_3DI = board.D19

PI_PIN_SOLA_BIO = board.D26
PI_PIN_NEOPIXELS = board.D21

PI_PIN_SOLA_FRIDGE = board.D20
PI_PIN_FRIDGE = board.D16

PI_PIN_SOLA_LIBQ = board.D12
PI_PIN_LIBQ1 = board.D25
PI_PIN_LIBQ2 = board.D24

PI_PIN_EXTRA = board.D18

PI_NEOPIXEL_COUNT = 5
FONTPATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Tick rate for sleeping between checking the buttons, 60 Hz
FRAME_TIME = 1.0/60.0

# surface code constants
N_DETERMINISTIC_SAMPLES = 3
DISTANCE = 3
N_AUX_QBS = DISTANCE**2 - 1  # Adjust this based on your actual number of auxiliary qubits
NEOPIXEL_COUNT = 17  # Adjust this based on your actual number of NeoPixels
TWPA_CALIBRATED = False
green_gradients = [
    (0, 255, 0),
    (4, 251, 0),
    (8, 247, 0),
    (12, 243, 0),
    (16, 239, 0),
    (20, 235, 0),
    (24, 231, 0),
    (28, 227, 0),
    (32, 223, 0),
    (36, 219, 0),
    (44, 211, 0),
    (48, 207, 0),
    (52, 203, 0),
    (56, 199, 0),
    (60, 195, 0),
    (64, 191, 0),
    (68, 187, 0),
    (72, 183, 0),
    (76, 179, 0),
    (80, 175, 0),
    (84, 171, 0),
    (88, 167, 0),
    (92, 163, 0),
    (96, 159, 0),
    (100, 155, 0),
    (104, 151, 0),
    (108, 147, 0),
    (112, 143, 0),
    (116, 139, 0),
    (120, 135, 0),
    (124, 131, 0),
    (128, 127, 0),
    (132, 123, 0),
    (136, 119, 0),
    (140, 115, 0),
    (144, 111, 0),
    (148, 107, 0),
    (152, 103, 0),
    (156, 99, 0),
    (160, 95, 0),
    (164, 91, 0),
    (168, 87, 0),
    (172, 83, 0),
    (176, 79, 0),
    (180, 75, 0),
    (184, 71, 0),
    (188, 67, 0),
    (192, 63, 0),
    (196, 59, 0),
    (200, 55, 0),
    (204, 51, 0),
    (208, 47, 0),
    (212, 43, 0),
    (216, 39, 0),
    (220, 35, 0),
    (224, 31, 0),
    (228, 27, 0),
    (232, 23, 0),
    (236, 19, 0),
    (240, 15, 0),
    (244, 11, 0),
    (248, 7, 0),
    (255, 3, 0)
]
blue_gradients = [
    (173, 216, 230), (176, 224, 230), (184, 233, 238), (188, 238, 243),
    (193, 240, 244), (197, 245, 249), (200, 249, 255), (202, 252, 255),
    (206, 253, 255), (210, 255, 255), (214, 255, 255), (178, 223, 238),
    (149, 206, 251), (120, 188, 255), (91, 171, 255), (62, 154, 255),
    (33, 136, 255), (4, 119, 255), (0, 104, 235), (0, 89, 204),
    (0, 74, 173), (0, 59, 143), (0, 44, 112), (0, 29, 81),
    (135, 206, 250), (127, 199, 242), (118, 192, 234), (110, 185, 226),
    (101, 178, 218), (93, 171, 210), (85, 164, 202), (76, 157, 194),
    (68, 150, 186), (59, 143, 178), (51, 136, 170), (43, 129, 162),
    (34, 122, 154), (26, 115, 146), (17, 108, 138), (9, 101, 130),
    (0, 94, 122), (0, 87, 114), (0, 80, 106), (0, 73, 98),
    (0, 66, 90), (0, 59, 82), (0, 52, 74), (0, 45, 66),
    (0, 38, 58), (0, 31, 50), (0, 24, 42), (0, 17, 34),
    (0, 10, 26), (0, 3, 18), (0, 0, 10), (0, 0, 20),
    (0, 0, 30), (0, 0, 40), (0, 0, 50), (0, 0, 60),
    (0, 0, 70), (0, 0, 80), (0, 0, 90), (0, 0, 100),
    (0, 0, 110), (0, 0, 120), (0, 0, 130), (0, 0, 140),
    (0, 0, 150), (0, 0, 160), (0, 0, 170), (0, 0, 180)
]
red_gradients = [(255//3, 0//4, 0//4)]*64
# COLOR_Z_AUX_QB = green_gradients[10]
# COLOR_X_AUX_QB = blue_gradients[20]
# COLOR_DATA_QB = red_gradients[0]
COLOR_Z_AUX_QB = (0, 128, 0)
COLOR_X_AUX_QB = (0, 0, 128)
COLOR_DATA_QB = (128, 0, 0)
# Other global variables
current_frame = 0

class PhDHat:

    def __init__(self):
        # configure software bypass. Set to False to run in normal mode with the hat
        self.software_bypass = False

        self.state = "pre-initialize"
        self.pixels = neopixel.NeoPixel(
            PI_PIN_NEOPIXELS,
            PI_NEOPIXEL_COUNT,
            brightness=0.2,
            # auto_write=False,
            pixel_order=neopixel.GRB,
        )
        # Create the I2C interface.
        self.i2c = busio.I2C(board.SCL, board.SDA)
        # Create the SSD1306 OLED class.
        self.disp_width = 128
        self.disp_height = 64
        self.disp = adafruit_ssd1306.SSD1306_I2C(
            self.disp_width,
            self.disp_height,
            self.i2c,
        )
        self.draw = None
        self.image = None

        # Font for text display
        self.font =  ImageFont.truetype(FONTPATH, 15)

        # Create the buttons
        # Default state is high (True)
        self.button_a = DigitalInOut(board.D5)
        self.button_b = DigitalInOut(board.D6)
        self.button_l = DigitalInOut(board.D27)
        self.button_r = DigitalInOut(board.D23)
        self.button_u = DigitalInOut(board.D17)
        self.button_d = DigitalInOut(board.D22)
        # Joystick center button
        self.button_c = DigitalInOut(board.D4)

        # SOLA IO
        self.sola_three_di_input = DigitalInOut(PI_PIN_SOLA_3DI)
        self.sola_bio_input = DigitalInOut(PI_PIN_SOLA_BIO)
        # could directly provide power to IC circuit ?
        self.sola_fridge_input = DigitalInOut(PI_PIN_SOLA_FRIDGE)
        self.sola_libqudev_input = DigitalInOut(PI_PIN_SOLA_LIBQ)

        # 3Di IO
        self.three_di_input = DigitalInOut(PI_PIN_3DI)

        # LibQudev IO
        self.libqudev01_input = DigitalInOut(PI_PIN_LIBQ1)
        self.libqudev02_input = DigitalInOut(PI_PIN_LIBQ2)

        # Bio IOs
        # none

        # Fridge IOs
        self.fridge_input = DigitalInOut(PI_PIN_FRIDGE)

        inputs = [
            self.button_a,
            self.button_b,
            self.button_l,
            self.button_r,
            self.button_u,
            self.button_d,
            self.button_c,
            self.sola_three_di_input,
            self.sola_bio_input,
            self.sola_fridge_input,
            self.sola_libqudev_input,
            self.libqudev01_input,
            self.libqudev02_input,
            self.fridge_input
        ]
        for inp in inputs:
            inp.direction = Direction.INPUT
            inp.pull = Pull.UP
            # Ground the pin to bring the value low (False)

        # Clear the display
        self.disp.fill(0)
        self.disp.show()

        # Clear the neopixels
        self.pixels.fill((0, 0, 0))
        # self.pixels.show()

        self.led_indices = {
            "d1":  1,
            "d2":  5,
            "d3":  7,
            "d4":  3,
            "d5":  9,
            "d6": 15,
            "d7": 11,
            "d8": 13,
            "d9": 17,
            "x1":  6,
            "x2":  4,
            "x3": 14,
            "x4": 12,
            "z1": 2,
            "z2": 10,
            "z3":  8,
            "z4": 16,
            "twpa1": 18,
            "twpa2": 19,
            "twpa3": 20,
        }


    def _display_text_on_screen(
        self, text: str, new_screen=True, font: ImageFont = None,
            font_size: None = None, position: tuple = None, anchor="mm",
            sleep: int = 0
    ) -> None:
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp.width
        height = self.disp.height
        print(text)
        if new_screen:
            # Fill with black by default
            self.image = Image.new("1", (width, height), color=0)

            # Get drawing object to draw on image.
            self.draw = ImageDraw.Draw(self.image)
            # Draw a black filled box to clear the image.
            # self.draw.rectangle((0, 0, width, height), outline=1, fill=1)

        if font_size is not None:
            font = ImageFont.truetype(FONTPATH, font_size)
        elif font is None:
            font = self.font
        if position is None:
            position = (self.disp_width / 2, self.disp_height / 2)

        self.draw.text(
            position,
            text,
            font=font,
            anchor=anchor,
            fill=1,  # white text
        )

        self.disp.image(self.image)
        self.disp.show()

        if sleep:
            time.sleep(sleep)

    def _display_surface_board_cycle(
            self, score: int, n_rounds: int, streak: int,
            cycle: int,
    ) -> None:
        text = f"Score: {score}/{n_rounds}\nStreak: {streak}"
        position=(40, 18)
        self._display_text_on_screen(
            text, new_screen=True,
            font_size=11, position=position,
        )

        self._display_text_on_screen(
            f'Cycle: {cycle}', new_screen=False,
            position=(64, 40)
        )
        self._display_text_on_screen(
            'L/R to scroll',
            new_screen=False,
            anchor=("lb"),
            font_size=11,
            position=(2, 64-2)
        )
        # time.sleep(2)

    def _led_test(self):
        self.pixels.fill((255, 0, 0))
        # self.pixels.show()
        time.sleep(2)
        self.pixels.fill((0, 255, 0))
        # self.pixels.show()
        time.sleep(2)
        self.pixels.fill((0, 0, 255))
        # self.pixels.show()
        time.sleep(2)
        for led_key in self.led_indices:
            self.pixels.fill((0, 0, 0))
            if led_key[0] == 'd':
                # red
                color = (255, 0, 0)
            elif led_key[0] == 'x':
                # blue
                color = (0, 0, 255)
            elif led_key[0] == 'z':
                # green
                color = (0, 255, 0)
            else:
                color = (128, 128, 128)
            # for pix_idx in range(len(self.pixels)):
            #     self.pixels[pix_idx] = (0, 0, 0)
            print(f"LED {led_key}, index {self.led_indices[led_key]}")
            self.pixels[self.led_indices[led_key]] = color
            # self.pixels.show()
            # mask = PI_NEOPIXEL_COUNT * [False]
            # colors = PI_NEOPIXEL_COUNT * [(0, 0, 0)]
            # mask[self.led_indices[led_key]] = True
            # colors[self.led_indices[led_key]] = color
            # self.light_neopixels(mask, colors)
            time.sleep(3)

    def initial_stage(self):
        print('Initial stage ...')
        # Display welcome text
        self._display_text_on_screen(
            "Welcome\nto your PhD hat\nPress #5 to start",
            sleep=1,
        )
        self.pixels.fill((0, 0, 0))
        # self._led_test()
        while True:
            # If A button pressed (value brought low)
            if not self.button_a.value:
                return
            elif self.check_bypasses():
                return
            else:
                time.sleep(FRAME_TIME)

    def three_di_stage(self):
        # Display message
        self._display_text_on_screen(
            "1. Fix flip-chip hat",
            sleep=3
        )
        self.pixels.fill((0, 0, 0))

        while True:
            # If 3di connection made (value brought low)
            if not self.three_di_input.value:
                return
            # bypass If A and B pressed (brought low)
            elif self.check_bypasses():
                return
            else:
                time.sleep(FRAME_TIME)

    def bio_stage(self):
        # Light all LEDs yellow to match the figure
        # for led_key in self.led_indices:
        #     self.pixels[self.led_indices[led_key]] = (128, 128, 0)
        # Display message
        self._display_text_on_screen(
            "2. Tune\nQubit frequencies", sleep=3,
        )
        success = False

        while not success:
            # @sasha, write code here


            time.sleep(FRAME_TIME)
            success = self.check_bypasses()



        # twpa optimization
        # params = dict(power=8.5, freq=7.90)  # easy ones
        # params = dict(power=8.0, freq=8.03)  # hard ones
        # target_gain = 20
        # fact = 40/12.13
        # success = False
        # while not success:
        #     text = (f"Pump parameters\n"
        #             f"Power (U/D): {params['power']:.1f} dBm\n"
        #             f"Freq.   (L/R): {params['freq']:.2f} GHz")
        #     gain, toomuchnoise = self.twpa_optimization(
        #         params['power'], params['freq'])
        #     self.pixels.fill((0, 0, 0))
        #     if not toomuchnoise:
        #         color = (int(15*gain), int(15*gain), 0)
        #         self.pixels.fill(color)
        #     else:
        #         for i in range(len(self.pixels)):
        #             color = [random.randrange(255) for i in range(3)]
        #             self.pixels[i] = color
        #     self._display_text_on_screen(
        #         text, position=(64, 20), font_size=11)
        #     # multiplicative factor such that 20 dB at "optimal" twpa parameters i.e. 9 dbm and 7.91 GHz
        #     text = f"Gain: {gain * fact:.2f} dB"
        #     self._display_text_on_screen(
        #         text,
        #         position=(64, 50),
        #         new_screen=False,
        #     )
        #     mapping = [
        #          (self.button_l, ('freq', -0.01), ),
        #          (self.button_r, ('freq', 0.01), ),
        #          (self.button_d, ('power', -0.1), ),
        #          (self.button_u, ('power', 0.1),)
        #      ]
        #     action = self.check_buttons(
        #         button_action_mapping=mapping, bypass_value=('power', 0.1))
        #     if isinstance(action, tuple):
        #         params[action[0]] += action[1]
        #     if not toomuchnoise and np.abs(gain * fact - target_gain) < 0.5:
        #         success = True
        #
        #     if toomuchnoise:
        #         pass # optionally  implement crazy mode
                #self._display_text_on_screen("Too much noise!", new_screen=False)



    def play_again(self):
        print('Play again?')
        # Display welcome text
        self._display_text_on_screen(
            "Play again?\nPress #5 to start",
            sleep=1,
        )
        self.pixels.fill((0, 0, 0))
        # self._led_test()
        while True:
            # If A button pressed (value brought low)
            if not self.button_a.value:
                N_DETERMINISTIC_SAMPLES = 0
                return True
            elif self.check_bypasses():
                N_DETERMINISTIC_SAMPLES = 0
                return True
            else:
                time.sleep(FRAME_TIME)

    def fridge_stage(self):
        self._display_text_on_screen(
            "3. Fix fridge cooldown\nOh my, a valve maybe?"
        )

        while True:
            # If fridge connection made (True = HIGH = 3.3v)
            if self.fridge_input.value:
                return
            # bypass If A and B pressed (brought low)
            elif self.check_bypasses():
                return
            else:
                time.sleep(FRAME_TIME)

    def libqudev_stage(self):
        self._display_text_on_screen(
            "4. Fix Libqudev!"
        )
        while True:
            # If 00 returned by libqudev (value brought low)
            if not self.libqudev01_input.value and not self.libqudev02_input:
                return
            # bypass If A and B pressed (brought low)
            elif self.check_bypasses():
                return
            else:
                time.sleep(FRAME_TIME)

    def finish_stage(self):
        self._display_text_on_screen(
            "You made it!\nCode: 123"
        )
        print('Game over.')


        #
        # return False  # Unsuccessful display
    def check_buttons(self, button_action_mapping=None, bypass_value="exit"):
        if button_action_mapping is None:
            button_action_mapping = [(self.button_r, 'next'), (self.button_l, 'prev')]
        for b, action in button_action_mapping:
            if not b.value:
                return action
        if self.check_bypasses():
            return bypass_value

    def check_bypasses(self, button_bypass=True, software_bypass=False):
        if button_bypass and not self.button_a.value and not self.button_b.value:
            return True
        elif software_bypass and self.software_bypass:
            print('software bypass will be activated in 2 sec!')
            time.sleep(2)
            return True
        else:
            return False

    def light_neopixels(self, mask, colors, indices=None, keys=None):
        """
        :param mask: list of booleans, if True, turn on pixel, if False, turn off
        :param colors: colors for each pixel. must be same length as mask
        :param indices: optional list of indices in the self.pixels list addressed by mask.
        must be same length as mask and colors
        :return:
        """
        # self.pixels.fill((0, 0, 0))
        if keys is not None:
            for k, m, c in zip(keys, mask, colors):
                if m:
                    self.pixels[self.led_indices[k]] = c  # Turn on NeoPixel
                else:
                    self.pixels[self.led_indices[k]] = (0, 0, 0)  # Turn off NeoPixel
        else:
            if indices is None:
                indices = np.arange(len(mask))
            for i, m, c in zip(indices, mask, colors):
                if m:
                    self.pixels[i] = c  # Turn on NeoPixel
                else:
                    self.pixels[i] = (0, 0, 0)  # Turn off NeoPixel

    # def display_logical_operator_prompt(self, op="Z"):
    #     txt = f"Flip {op}_L?\n(Up/Down: Yes/No)"
    #     self._display_text_on_screen(txt, font_size=12)
    #
    # def display_success_screen(self, score, streak):
    #     text = f"Success!\nNew Score: {score}\nStreak: {streak}"
    #     self._display_text_on_screen(text, font_size=12)
    #     self.light_neopixels([False] + 17*[True], [(0, 0, 0)] + 17*[(0, 255, 0)])  # green
    #     time.sleep(2)
    #
    # def display_failure_screen(self, score):
    #     text = f"Incorrect :-(\nScore: {score}"
    #     self._display_text_on_screen(text, font_size=12)
    #     self.light_neopixels([False] + 17*[True], [(0, 0, 0)] + 17*[(255, 0, 0)])  # red
    #     time.sleep(2)
