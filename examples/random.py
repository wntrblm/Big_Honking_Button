# This example shows how to load multiple samples and
# select one at random to play when the button is pressed.

import random
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

samples = [
    bhb.load_sample("samples/kick.wav"),
    bhb.load_sample("samples/snare.wav"),
    bhb.load_sample("samples/clap.wav"),
]

while bhb.update():
    if bhb.triggered:
        bhb.gate_out = True
        bhb.play(random.choice(samples), pitch_cv=bhb.pitch_in)

    if bhb.released:
        bhb.gate_out = False
