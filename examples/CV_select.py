# Sample player that holds multiple samples.
# The CV input selects which sample is plays.

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

samples = [
  bhb.load_sample("samples/clap.wav"),
  bhb.load_sample("samples/dist.wav"),
  bhb.load_sample("samples/go.wav"),
  bhb.load_sample("samples/honk.wav"),
  bhb.load_sample("samples/kick.wav"),
  bhb.load_sample("samples/reverse.wav"),
  bhb.load_sample("samples/snare.wav")
]

num_samples = len(samples)
pitch_in_min = -2.5
pitch_in_max = 2.5

while True:
    if bhb.triggered:
        bhb.gate_out = True
        sample_index = int( ( ( (bhb.pitch_in - pitch_in_min) * num_samples) / (pitch_in_max - pitch_in_min) ) - (num_samples / 2 ) )
        sample = samples[sample_index]
        bhb.play(sample)

    if bhb.released:
        bhb.gate_out = False
