# This advanced example shows how to create a custom waveform
# for the button to output. In this case, it generates a
# sine wave. You can use this example as a basis for very
# basic oscillators.
# See also noise.py

import array
import math
import audiocore
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()


# This generates a raw set of samples that represents one full
# cycle of a sine wave. If you wanted different waveforms, you
# could change the formula here to generate that instead.
def generate_sine_wave(volume=1.0):
    volume = volume * (2 ** 15 - 1)  # Increase this to increase the volume of the tone.
    length = 100
    samples = array.array("H", [0] * length)

    for i in range(length):
        samples[i] = int((1 + math.sin(math.pi * 2 * i / length)) * volume)

    return samples

sine_wave = generate_sine_wave(0.8)
sample = audiocore.RawSample(sine_wave)

# Change this to play different notes. You can also
# check the CV input using `bhb.pitch_in` and re-adjust
# the sample rate.
frequency = 440
sample.sample_rate = frequency * len(sine_wave)


while bhb.update():
    if bhb.triggered:
        bhb.gate_out = True
        bhb.play(sample, loop=True)

    if bhb.released:
        bhb.gate_out = False
        bhb.stop()
