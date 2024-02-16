# This example shows how to play a different sample when the button is
# pressed and when the button is released.

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

snare = bhb.load_sample("samples/snare.wav")
reverse = bhb.load_sample("samples/reverse.wav")

while bhb.update():
    if bhb.triggered:
        bhb.gate_out = True
        bhb.play(snare)

    if bhb.released:
        bhb.gate_out = False
        bhb.play(reverse)
