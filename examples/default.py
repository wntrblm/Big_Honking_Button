# This is the default program that comes on the Big Honking Button.
# It makes a honk sound when the button is pressed (or the gate
# is triggered) and you can change the honk sound's pitch using
# the CV input.

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()
sample = bhb.load_sample("samples/honk.wav")

while True:
    if bhb.triggered:
        bhb.gate_out = True
        bhb.play(sample, pitch_cv=bhb.pitch_in)

    if bhb.released:
        bhb.gate_out = False
        # Uncomment the call to stop to make the sample
        # stop playing as soon as you release the button.
        # bhb.stop()
