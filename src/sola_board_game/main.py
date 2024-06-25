import phdhat

# Set up system
hat = phdhat.PhDHat()

hat.initial_stage()
hat.sola_stage(phdhat.SOLA.THREE_DI) # ok
hat.three_di_stage()
hat.sola_stage(phdhat.SOLA.BIO) # not ok (open)
hat.bio_stage()

# tested
hat.sola_stage(phdhat.SOLA.FRIDGE)
hat.fridge_stage()

#
hat.sola_stage(phdhat.SOLA.LIBQUDEV) # not ok (open)
hat.libqudev_stage()

hat.finish_stage()
# keep_playing = hat.play_again()
# while keep_playing:
#     hat.surface_code_stage()
