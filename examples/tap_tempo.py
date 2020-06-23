# This example shows how to use the button as a means of
# setting a tempo and continuously triggering a sample
# a sample based on the tapped out tempo on the button
# (or via the gate input).

import time
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()
sample = bhb.load_sample("samples/kick.wav")

# The interval determines how many seconds
# between samples. At startup, it'll play
# the sample once every half second.
interval = 0.5  # seconds

# This keeps track of the last time the
# sample was played.
last_sample_played = time.monotonic()

# This keeps track of the last time the
# button was pressed. On startup, it's
# just set to the current time, but
# it doesn't really matter.
last_button_press = time.monotonic()


while True:
    # Get the current time and see if enough
    # time has passed to play the sample.
    now = time.monotonic()
    if now > last_sample_played + interval:
        last_sample_played = now
        bhb.play(sample)
        bhb.gate_out = True
    else:
        bhb.gate_out = False

    # If the button is pressed (or gate in
    # is triggered), the figure out the time
    # between this press and the last press
    # and use that as the tempo.
    if bhb.triggered:
        interval = now - last_button_press
        last_button_press = now
