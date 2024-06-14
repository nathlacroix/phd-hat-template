import numpy as np
from PIL import ImageDraw, Image


class FreqPlot:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.buffer = 16
        
        self.main_img = Image.new("1", (self.w, self.h))
        self.main_draw = ImageDraw.Draw(self.main_img)
        
        self.nb_qb = 3
        self.qb1_freq = 0.3
        self.qb2_freq = 0.8
        self.qb3_freq = 0.1
        
        self.hybridization = 0.2
        
        self.build_main_frame()
        
    def build_main_frame(self):
        qb_width = (self.w - self.buffer)//self.nb_qb
        # Clear the main image
        self.main_draw.rectangle((0,0,self.w,self.h), fill=0, outline=0)

        # Set qubit labels
        for qb_idx in range(self.nb_qb):
            self.main_draw.text((self.buffer + qb_width/4 + qb_idx * qb_width, 0), f'Qb{qb_idx + 1}', fill=1)
            
        ylabel_img = self.build_ylabel()
        self.main_img.paste(ylabel_img, (0, int(-0.5*self.buffer)))
        
    
    def update_freq_plot(self):
        # Prepare the plot part of the img
        pw = self.w - self.buffer
        ph = self.h - self.buffer
        qb_width = pw/self.nb_qb
        qb_bar_width = 2
        
        plot_img = Image.new("1", (pw, ph))
        plot_draw = ImageDraw.Draw(plot_img)

        # Clear the plot
        plot_draw.rectangle((0,0, pw, ph), fill=0, outline=1)

        # Draw a big rect for each qubit
        for qb in range(self.nb_qb):
            plot_draw.rectangle((qb * qb_width, 0, (qb + 1) * qb_width, ph), fill=0, outline=1)

        # Now insert a qb bar for each qubit
        plot_draw.rectangle((0, self.qb1_freq * ph, qb_width, self.qb1_freq * ph + qb_bar_width), 
                            fill=1, outline=1)
        plot_draw.rectangle((qb_width, self.qb2_freq * ph, 2 * qb_width, self.qb2_freq * ph + qb_bar_width), 
                            fill=1, outline=1)
        plot_draw.rectangle((2 * qb_width, self.qb3_freq * ph, 3 * qb_width, self.qb3_freq * ph + qb_bar_width),
                            fill=1, outline=1)

        # Show hybridization if necessary
        if self.qb1_freq == self.qb2_freq:
            # Dark state img
            dark_state_img = Image.new("1", (int(qb_width), 5*qb_bar_width))
            dark_state_draw = ImageDraw.Draw(dark_state_img)
            dark_state_draw.rectangle((0,0, qb_width, 3*qb_bar_width), fill=0, outline=1)
            dark_state_draw.text((0, 0), '|D>', fill=1)

            bright_state_img = Image.new("1", (int(qb_width),5* qb_bar_width))
            bright_state_draw = ImageDraw.Draw(bright_state_img)
            bright_state_draw.rectangle((0,0, qb_width, 5*qb_bar_width), fill=1, outline=1)
            bright_state_draw.text((0, 0), '|B>', fill=0)

            plot_img.paste(dark_state_img, (int(qb_width/2), int((self.qb1_freq + self.hybridization) * ph)))
            plot_img.paste(bright_state_img, (int(qb_width/2), int((self.qb1_freq - self.hybridization) * ph)))
        
        self.main_img.paste(plot_img, (self.buffer, self.buffer))

        
    def build_ylabel(self):
        # Create Y-label (rotation seem to only be possible for images, so do it in a weird way)
        ylabel_img = Image.new("1", (self.h, self.buffer))  # diminsions exchange dueto upcomming rotation
        ylabel_draw = ImageDraw.Draw(ylabel_img)
        ylabel_draw.text((0,0), 'Freq, a.u.', fill=1, outline=1)
        ylabel_img = ylabel_img.rotate(90, expand=True)       
        
        return ylabel_img
    

