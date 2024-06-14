import time

import adafruit_ssd1306
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import neopixel
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from gpiozero import DistanceSensor

from bio import value_to_rgb, FreqPlot, NoisePlot

PI_PIN_SOLA_3DI = board.D13
PI_PIN_3DI = board.D19
PI_PIN_3DI2 = board.D26


PI_PIN_SOLA_BIO = board.D21
PI_PIN_NEOPIXELS = board.D21

PI_PIN_SOLA_FRIDGE = board.D16
PI_PIN_FRIDGE = board.D12

PI_PIN_SOLA_LIBQ = board.D25
PI_PIN_LIBQ1 = board.D24
PI_PIN_LIBQ2 = board.D18

PI_PIN_EXTRA = board.D18

FONTPATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Tick rate for sleeping between checking the buttons, 60 Hz
FRAME_TIME = 1.0/60.0

# surface code constants
N_DETERMINISTIC_SAMPLES = 3
DISTANCE = 3
N_AUX_QBS = DISTANCE**2 - 1  # Adjust this based on your actual number of auxiliary qubits
NEOPIXEL_COUNT = 5  # Adjust this based on your actual number of NeoPixels

class SOLA:
    THREE_DI = 1
    BIO = 2
    FRIDGE = 3
    LIBQUDEV = 4

    PINS = {THREE_DI: PI_PIN_SOLA_3DI,
             BIO: PI_PIN_SOLA_BIO,
             FRIDGE: PI_PIN_SOLA_FRIDGE,
             LIBQUDEV: PI_PIN_SOLA_LIBQ}


class PhDHat:

    def __init__(self):
        # configure software bypass. Set to False to run in normal mode with the hat
        self.software_bypass = False

        self.state = "pre-initialize"
        self.pixels = neopixel.NeoPixel(
            PI_PIN_NEOPIXELS,
            NEOPIXEL_COUNT,
            brightness=0.2,
            # auto_write=False,
            pixel_order=neopixel.GRBW,
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

        # for inp in [self.fridge_input]:
        for inp in [self.sola_bio_input, self.libqudev01_input, self.libqudev02_input]:
            inp.direction = Direction.INPUT
            inp.pull = Pull.DOWN
        # Clear the display
        self.disp.fill(0)
        self.disp.show()

        # Clear the neopixels
        self.pixels.fill((0, 0, 0))
        # self.pixels.show()

        self.led_indices = {
            "q3":  0,
            "dark": 1,
            "q1":  2,
            "bright":  3,
            "q2":  4,
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
        # self.pixels[0] = (255, 0, 0)
        # self.pixels[1] = (0, 255, 0)
        # self.pixels[2] = (0, 0, 255)
        # self.pixels[3] = (255, 255, 0)
        self.pixels[4] = (0, 255, 255)
        self.pixels.show()
        # time.sleep(2)
        # self.pixels.fill((0, 255, 0))
        # self.pixels.show()
        # time.sleep(2)
        # self.pixels.fill((0, 0, 255))
        # self.pixels.show()
        # time.sleep(2)
        # for led_key in self.led_indices:
        #     self.pixels.fill((0, 0, 0))
        #     if led_key[0] == 'q':
                # red
                # color = (255, 0, 0)
            # elif led_key[0] == 'd':
                # blue
                # color = (0, 0, 255)
            # elif led_key[0] == 'b':
                # green
                # color = (0, 255, 0)
            # else:
            #     color = (128, 128, 128)
            # for pix_idx in range(len(self.pixels)):
            #     self.pixels[pix_idx] = (0, 0, 0)
            # print(f"LED {led_key}, index {self.led_indices[led_key]}")
            # self.pixels[self.led_indices[led_key]] = color
            # self.pixels.show()
            # mask = PI_NEOPIXEL_COUNT * [False]
            # colors = PI_NEOPIXEL_COUNT * [(0, 0, 0)]
            # mask[self.led_indices[led_key]] = True
            # colors[self.led_indices[led_key]] = color
            # self.light_neopixels(mask, colors)
            # time.sleep(3)

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

    def sola_stage(self, pin):
        print(f'sola stage with pin {pin}...')
        msg = f'Run QudevSola\nleg #{pin}'
        match pin:
            case SOLA.THREE_DI:
                self._display_text_on_screen(msg)
                print('Waiting for connection to 3Di...')
                while True:
                    # If 3di connection made (value brought low)
                    if not self.sola_three_di_input.value:
                        print('Connection found!')
                        return
                    # bypass If A and B pressed (brought low)
                    elif self.check_bypasses():
                        return
                    else:
                        time.sleep(FRAME_TIME)
            case SOLA.BIO:
                self._display_text_on_screen(msg)
                print('Waiting for connection to Bio...')
                while True:
                    # If 3di connection made (value brought low)
                    if self.sola_bio_input.value:
                        print('Connection found!')
                        return
                    # bypass If A and B pressed (brought low)
                    elif self.check_bypasses():
                        return
                    else:
                        time.sleep(FRAME_TIME)
            case SOLA.FRIDGE:
                self._display_text_on_screen(msg)
                print('Waiting for connection to fridge...')
                while True:
                    # If 3di connection made (value brought low)
                    if not self.sola_fridge_input.value:
                        print('Connection found!')
                        return
                    # bypass If A and B pressed (brought low)
                    elif self.check_bypasses():
                        return
                    else:
                        time.sleep(FRAME_TIME)
            case SOLA.LIBQUDEV:
                self._display_text_on_screen(msg)
                print('Waiting for connection to libqudev...')
                while True:
                    # If 3di connection made (value brought low)
                    if not self.sola_libqudev_input.value:
                        print('Connection found!')
                        return
                    # bypass If A and B pressed (brought low)
                    elif self.check_bypasses():
                        return
                    else:
                        time.sleep(FRAME_TIME)

    def three_di_stage(self):
        # Display message
        self._display_text_on_screen(
            "1. Level flip\n-chip hat",
            sleep=3
        )
        # Define the GPIO pins for the HC-SR04 sensor
        TRIG = 19
        ECHO = 26

        # Set the GPIO mode
        ultrasonic = DistanceSensor(echo=ECHO, trigger=TRIG)

        # Define the distance range
        MIN_DISTANCE = 5  # Minimum distance in cm
        MAX_DISTANCE = 25  # Maximum distance in cm

        # Timer settings
        TIMER_DURATION = 10  # Countdown timer duration in seconds
        SUCCESS_STR = "Congrats, your sample is level."

        def measure_distance():
            """Measure the distance using the HC-SR04 sensor."""
            distance = ultrasonic.distance
            # Round and convert to str
            # Convert meters to centimeters
            distance_cm = distance * 100
            # Round to 1 decimal place and format as a string
            distance_cm_str = f"{distance_cm:.1f}"

            return distance, distance_cm_str

        output_str = ""
        countdown_timer = None
        countdown_start_time = None

        # Needs to be modified such that PRINT_FUNC prints the output_str
        while output_str != SUCCESS_STR:

            distance, distance_cm_str = measure_distance()

            if MIN_DISTANCE <= distance <= MAX_DISTANCE:
                if countdown_timer is None:
                    countdown_timer = TIMER_DURATION
                    countdown_start_time = time.time()
                    elapsed_time = time.time() - countdown_start_time
                    remaining_time = TIMER_DURATION - elapsed_time
                    output_str = f"Keep sample\nlevel.\nDistance: {distance_cm_str} cm, Timer: {int(remaining_time)}s"
                else:
                    elapsed_time = time.time() - countdown_start_time
                    remaining_time = TIMER_DURATION - elapsed_time
                    if remaining_time <= 0:
                        output_str = SUCCESS_STR
                    else:
                        output_str = f"Please keep sample level. Distance: {distance_cm_str} cm, Timer: {int(remaining_time)}s"
            else:
                countdown_timer = None
                countdown_start_time = None
                output_str = f" Sample not level. Distance: {distance_cm_str} cm."

            self._display_text_on_screen(output_str)
            time.sleep(1)

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
        # initialize
        # Clear display.
        self.disp.fill(0)
        self.disp.show()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        # test something
        width = self.disp.width
        height = self.disp.height

        # test_plot = FreqPlot(width, height, buffer=16, nb_pts=3)
        # test_plot.update_freq_plot()
        # self.disp.image(test_plot.main_img)
        # self.disp.show()
        print('width = %d' % width)
        print('height = %d' % height)

        freq_plot = FreqPlot(w=width, h=height, buffer=16, nb_pts=3)
        noise_plot = NoisePlot(w=width, h=height, buffer=16, nb_pts=28)
        self.disp.image(freq_plot.main_img)
        self.disp.show()
        success = False
        for label, freq in zip(freq_plot.labels, freq_plot.values):
            rgb = value_to_rgb(1 - freq) + (0,)
            self.light_up_pixel(self.led_indices[label], rgb)

        while not success:
            if not self.button_r.value:
                freq_plot.update_marker(1)

            if not self.button_l.value:
                freq_plot.update_marker(-1)

            if not self.button_u.value:
                freq_plot.update_value(-0.1)
                for label, freq in zip(freq_plot.labels, freq_plot.values):
                    rgb = value_to_rgb(1-freq) + (0,)
                    self.light_up_pixel(self.led_indices[label], rgb)

            if not self.button_d.value:
                freq_plot.update_value(0.1)
                for label, freq in zip(freq_plot.labels, freq_plot.values):
                    rgb = value_to_rgb(1-freq) + (0,)
                    self.light_up_pixel(self.led_indices[label], rgb)

            if freq_plot.values[0] == freq_plot.values[1]:
                self.light_up_pixel(self.led_indices['bright'], (255, 255, 255, 255))
                rgb_dark = value_to_rgb(1-(freq_plot.values[1] + freq_plot.hybridization)) + (0,)

                self.light_up_pixel(self.led_indices['dark'], tuple(i//20 for i in rgb_dark))
                # Game 1 done
                if freq_plot.values[2] == freq_plot.values[1] + freq_plot.hybridization:
                    print('First game done!')
                    success_img = Image.new('1', (width, height))
                    success_draw = ImageDraw.Draw(success_img)
                    success_draw.text((16, 32), 'First game done! :)', fill=1)
                    self.disp.image(success_img)
                    self.disp.show()
                    time.sleep(5)
                    success = True

            self.disp.image(freq_plot.main_img)
            self.disp.show()
            if self.check_bypasses():
                break


        self.disp.image(noise_plot.main_img)
        self.disp.show()
        time.sleep(2)
        success = False

        while not success:
            print('second game')
            if not self.button_r.value:
                noise_plot.update_marker(1)

            if not self.button_l.value:
                noise_plot.update_marker(-1)

            if not self.button_u.value:
                noise_plot.update_value(-0.1)

            if not self.button_d.value:
                noise_plot.update_value(0.1)

            self.disp.image(noise_plot.main_img)
            self.disp.show()
            # TO BE IMPLEMENTED: success check
            success = self.check_bypasses()
            time.sleep(FRAME_TIME)

    def light_up_pixel(self, index, color):
        print(f"Lighting up pixel {index} with color {color}.")
        self.pixels[index] = color
        self.pixels.show()
        time.sleep(0.1)  # Add a delay to see the change



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
            # If fridge connection made (value brought low)
            if self.fridge_input.value:
                print('cooldown initiated')
                time.sleep(5)
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
            # both need to be configured in pull down mode
            # If 11 returned by libqudev (value brought low)
            if self.libqudev01_input.value and self.libqudev02_input:
                self._display_text_on_screen(
                    "Success, you\nmastered libqudev"
                )
                return
            if self.libqudev01_input.value and not self.libqudev02_input:
                self._display_text_on_screen(
                    "Error: string contains\nillegal characters"
                )
            if not self.libqudev01_input.value and not self.libqudev02_input:
                self._display_text_on_screen(
                    "Error: dupplicate\ncell name"
                )
            if not self.libqudev01_input.value and not self.libqudev02_input:
                print('value returned: 00 (no input)')
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
            print('button bypass activated!')
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
