# This example shows how to play a different sample depending on if the
# button is pressed or the gate in is triggered.

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

snare = bhb.load_sample("samples/snare.wav")
clap = bhb.load_sample("samples/clap.wav")

while bhb.update():
    if bhb.button.pressed:
        bhb.play(snare)
    elif bhb.gate_in.triggered:
        bhb.play(clap)
