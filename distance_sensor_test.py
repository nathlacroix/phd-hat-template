from gpiozero import DistanceSensor
import time

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
            output_str = f"Please keep sample level.\n Distance: {distance_cm_str} cm, Timer: {int(remaining_time)}s"
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

    print(output_str)
    time.sleep(1)  # Delay to avoid rapid polling