import numpy as np
from PIL import ImageDraw, Image, ImageFont


class Plot:
    def __init__(self, w, h, buffer, nb_pts):
        self.w = w
        self.h = h
        self.buffer = buffer
        self.nb_pts = nb_pts

        self.main_img = Image.new("1", (self.w, self.h))
        self.main_draw = ImageDraw.Draw(self.main_img)

        self.marker = 0
        self.values = None

    def update_marker(self, mark_step):
        self.marker += mark_step
        self.marker %= self.nb_pts

    def update_value(self, value_step, update=True):
        self.values[self.marker] = round(self.values[self.marker] + value_step, 1)
        if update:
            self.update_graph_plot()

    def update_graph_plot(self):
        """
        Define in childs
        :return: Nothing
        """
        pass

    def build_ylabel(self, text):
        # Create Y-label (rotation seem to only be possible for images, so do it in a weird way)
        ylabel_img = Image.new("1", (self.h, self.buffer))  # diminsions exchange dueto upcomming rotation
        ylabel_draw = ImageDraw.Draw(ylabel_img)
        ylabel_draw.text((0, 0), text=text, fill=1, outline=1)
        ylabel_img = ylabel_img.rotate(90, expand=True)

        return ylabel_img


class FreqPlot(Plot):
    def __init__(self, w, h, buffer, nb_pts):
        super().__init__(w, h, buffer, nb_pts)

        self.values = [0.1, 0.8, 0.3]
        self.labels = ['q1', 'q2', 'q3']
        self.hybridization = 0.3

        self.build_main_frame()
        self.update_graph_plot()

    def build_main_frame(self):
        qb_width = (self.w - self.buffer) // self.nb_pts
        # Clear the main image
        self.main_draw.rectangle((0, 0, self.w, self.h), fill=0, outline=0)

        # Set qubit labels
        for qb_idx in range(self.nb_pts):
            self.main_draw.text((self.buffer + qb_width / 4 + qb_idx * qb_width, 0), f'Qb{qb_idx + 1}', fill=1)

        ylabel_img = self.build_ylabel(text='Freq. a.u.')
        # ylabel_img = ylabel_img.rotate(90, expand=True)
        self.main_img.paste(ylabel_img, (0, - int(0.5 * self.buffer)))

    # def update_freq(self, freq_step):
    #     self.freqs[self.marker] = round(self.freqs[self.marker] + freq_step, 1)
    #     self.update_freq_plot()

    def update_graph_plot(self):
        # Prepare the plot part of the img
        pw = self.w - self.buffer
        ph = self.h - self.buffer
        qb_width = pw / self.nb_pts
        qb_bar_width = 5

        plot_img = Image.new("1", (pw, ph))
        plot_draw = ImageDraw.Draw(plot_img)

        # Clear the plot
        plot_draw.rectangle((0, 0, pw, ph), fill=0, outline=1)

        # Draw a big rect for each qubit
        for qb in range(self.nb_pts):
            plot_draw.rectangle((qb * qb_width, 0, (qb + 1) * qb_width, ph), fill=0, outline=1)

        # Now insert a qb bar for each qubit
        plot_draw.rectangle((0, self.values[0] * ph, qb_width, self.values[0] * ph + qb_bar_width),
                            fill=1, outline=1)
        plot_draw.rectangle((qb_width, self.values[1] * ph, 2 * qb_width, self.values[1] * ph + qb_bar_width),
                            fill=1, outline=1)
        plot_draw.rectangle((2 * qb_width, self.values[2] * ph, 3 * qb_width, self.values[2] * ph + qb_bar_width),
                            fill=1, outline=1)

        # Show hybridization if necessary
        if self.values[0] == self.values[1]:
            # Dark state img
            dark_state_img = Image.new("1", (int(qb_width), 2 * qb_bar_width))
            dark_state_draw = ImageDraw.Draw(dark_state_img)
            dark_state_draw.rectangle((0, 0, qb_width, 2 * qb_bar_width), fill=0, outline=1)
            dark_state_draw.text((10, 0), '|D>', fill=1)
            # dark_state_img = dark_state_img.resize((int(qb_width), int(1.5*qb_bar_width)), Image.ANTIALIAS)

            bright_state_img = Image.new("1", (int(qb_width), 2 * qb_bar_width))
            bright_state_draw = ImageDraw.Draw(bright_state_img)
            bright_state_draw.rectangle((0, 0, qb_width, 2 * qb_bar_width), fill=1, outline=0)
            bright_state_draw.text((10, 0), '|B>', fill=0)
            # bright_state_img = bright_state_img.resize((int(qb_width), int(1.5*qb_bar_width)), Image.ANTIALIAS)

            plot_img.paste(dark_state_img, (int(qb_width / 2), int((self.values[0] + self.hybridization) * ph)))
            plot_img.paste(bright_state_img, (int(qb_width / 2), int((self.values[0] - self.hybridization) * ph)))

        self.main_img.paste(plot_img, (self.buffer, self.buffer))


class NoisePlot(Plot):
    def __init__(self, w, h, buffer, nb_pts):
        super().__init__(w, h, buffer, nb_pts)

        self.values = [0.9] * (nb_pts)


        self.ypixels = 10
        self.xpixels = nb_pts

        self.omega = np.linspace(0, 200, self.xpixels)
        self.omegac = 100
        self.b = 5
        self.a = 2/10 * self.ypixels

        self.current_distance = self.distance(self.noise_spec())
        self.build_main_frame()
        self.update_graph_plot()

    def noise_spec(self):
        exp = (self.omega - self.omegac) ** 2 / (2 * np.pi * self.b) ** 2
        return self.a / (np.exp(exp) + 1)

    def distance(self, target):
        values = [(1 - v) - 0.1 for v in  self.values]
        print(target, values, target - values)
        norm = np.linalg.norm(target - values) / (0.5 * self.ypixels)
        if norm > 1:
            norm = 1
        return norm

    def build_main_frame(self):
        # Clear the img
        self.main_draw.rectangle((0, 0, self.w, self.h), fill=0, outline=0)
        # Put x label
        self.main_draw.text((2*self.buffer, self.h - self.buffer), text='Frequency, a.u.', fill=1)
        # Put y label
        ylabel_img = self.build_ylabel(text='S(w) a.u.')
        self.main_img.paste(ylabel_img, (0, - int(0.5 * self.buffer)))

    def update_graph_plot(self):
        w = self.w - self.buffer
        h = self.h - self.buffer

        bar_width = w/self.nb_pts
        power_plot = Image.new("1", (w, h))
        power_draw = ImageDraw.Draw(power_plot)

        for pidx, power in enumerate(self.values):
            power_draw.rectangle(xy=(pidx*bar_width, power*h, (pidx+1)*bar_width,  power*h + 5), fill=1, outline=0)

        self.main_img.paste(power_plot, (self.buffer, 0))

        self.current_distance = self.distance(self.noise_spec())



# LED part
def interpolate_rgb(start, end, factor):
    return start + (end - start) * factor


def frequency_to_rgb(frequency):
    # Frequency ranges in THz
    red_start = 400
    red_end = 484
    green_start = 484
    green_end = 610
    blue_start = 610
    blue_end = 789

    # Initialize RGB values
    r, g, b = 0, 0, 0

    if frequency < red_start:
        r, g, b = 255, 0, 0  # Dark red
    elif frequency <= red_end:
        factor = (frequency - red_start) / (red_end - red_start)
        r = interpolate_rgb(255, 255, factor)
        g = interpolate_rgb(0, 255, factor)
        b = interpolate_rgb(0, 0, factor)
    elif frequency <= green_end:
        factor = (frequency - green_start) / (green_end - green_start)
        r = interpolate_rgb(255, 0, factor)
        g = interpolate_rgb(255, 255, factor)
        b = interpolate_rgb(0, 0, factor)
    elif frequency <= blue_end:
        factor = (frequency - blue_start) / (blue_end - blue_start)
        r = interpolate_rgb(0, 0, factor)
        g = interpolate_rgb(255, 0, factor)
        b = interpolate_rgb(0, 255, factor)
    else:
        r, g, b = 0, 0, 255  # Dark blue

    return int(r), int(g), int(b)


def value_to_rgb(value):
    # Map value (0 to 1) to frequency (400 THz to 789 THz)
    min_freq = 400
    max_freq = 789
    frequency = min_freq + value * (max_freq - min_freq)
    return frequency_to_rgb(frequency)

