# This example determines which sample to play based on the
# pitch CV input- useful for things like drum samples.

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

samples = [
    bhb.load_sample("samples/clap.wav"),
    bhb.load_sample("samples/dist.wav"),
    bhb.load_sample("samples/go.wav"),
    bhb.load_sample("samples/honk.wav"),
    bhb.load_sample("samples/kick.wav"),
    bhb.load_sample("samples/reverse.wav"),
    bhb.load_sample("samples/snare.wav"),
]

while True:
    if bhb.triggered:
        # This selects a sample from the list based on the pitch CV input.
        # The samples are evenly distributed across the CV range,
        # -5v to +5v. So if you send -5v it'll select the first sample and
        # if you send +5v it'll select the last one, with voltages in-between
        # will select the closest sample in the list.
        sample = bhb.select_from_list_using_cv(samples, bhb.pitch_in)

        # By default, this uses the full CV range but you can change it by
        # specifying low and high - useful if you only have a positive CV
        # source.

        # sample = bhb.select_from_list_using_cv(samples, bhb.pitch_in, low=0, high=5)

        bhb.play(sample)
        bhb.gate_out = True

    if bhb.released:
        bhb.gate_out = False
