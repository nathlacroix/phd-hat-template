import board
import neopixel
import time

# Choose an open GPIO pin connected to the NeoPixel strip, e.g., board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21

# The number of NeoPixels
num_pixels = 5  # Adjust this to match the number of NeoPixels in your strip

# The order of the pixel colors - RGB or GRB. Some NeoPixels use RGBW (White).
ORDER = neopixel.GRBW

# Create the NeoPixel object
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

print(f"Initialized NeoPixels on pin {pixel_pin} with {num_pixels} pixels.")

# Function to light up the first pixel with a specific color
def light_up_pixel(index, color):
    print(f"Lighting up pixel {index} with color {color}.")
    pixels[index] = color
    pixels.show()
    time.sleep(3)  # Add a delay to see the change

# Example usage
try:
    while True:
        light_up_pixel(0, (0, 255, 0,0))
        light_up_pixel(1, (255, 0, 0,0))
        light_up_pixel(2, (255, 255, 255,0))
        light_up_pixel(3, (0, 0, 255,0))
        light_up_pixel(4, (255, 0, 0,0))
        # light_up_pixel(4, (0, 255, 255,0))  # Cyan

except KeyboardInterrupt:
    print("Exiting and clearing NeoPixels.")
    # Clear the NeoPixels on exit
    pixels.fill((0, 0, 0))
    pixels.show()
