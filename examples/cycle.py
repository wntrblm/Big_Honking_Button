# This example shows how to load multiple samples and
# cycle through them. Each time the button is pressed,
# it plays a sample and then advances to the next
# sample in the list.

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()


samples = [
    bhb.load_sample("samples/kick.wav"),
    bhb.load_sample("samples/snare.wav"),
    bhb.load_sample("samples/clap.wav"),
]

current_sample_no = 0

while bhb.update():
    if bhb.triggered:
        bhb.gate_out = True
        bhb.play(samples[current_sample_no], pitch_cv=bhb.pitch_in)
        current_sample_no += 1
        if current_sample_no >= len(samples):
            current_sample_no = 0

    if bhb.released:
        bhb.gate_out = False
