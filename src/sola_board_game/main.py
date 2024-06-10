import phdhat

# Set up system
hat = phdhat.PhDHat()

hat.initial_stage()
hat.three_di_stage()
hat.bio_stage()
hat.fridge_stage()
hat.libqudev_stage()
hat.finish_stage()
# keep_playing = hat.play_again()
# while keep_playing:
#     hat.surface_code_stage()
