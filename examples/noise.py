# This advanced sample is similar to the sine example, except
# it generates white noise.

import array
import random
import audiocore
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()


# This generates a raw set of samples that represents one full
# cycle of a sine wave. If you wanted different waveforms, you
# could change the formula here to generate that instead.
def generate_noise(volume=1.0):
    volume = volume * (2 ** 15 - 1)  # Increase this to increase the volume of the tone.
    length = 800
    samples = array.array("H", [0] * length)

    for i in range(length):
        samples[i] = int(random.random() * volume)
    
    return samples

noise = generate_noise(0.8)
sample = audiocore.RawSample(noise)

# Change this to set the noise sample's frequency.
# This generate works well as pretty low numbers,
# but you can get some interesting effects at higher
# values.
frequency = 2
sample.sample_rate = frequency * len(noise)


while True:
    if bhb.triggered:
        bhb.gate_out = True
        bhb.play(sample, loop=True)

    if bhb.released:
        bhb.gate_out = False
        bhb.stop()