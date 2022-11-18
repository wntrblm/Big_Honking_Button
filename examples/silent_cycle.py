#cycle through your samples with the button (silently)
#trigger the sample with the trigger input 

import os
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()
samples = []
path_of_the_directory = '/samples'

for files in os.listdir(path_of_the_directory):
    if files.endswith('.wav'):
        samples.append(bhb.load_sample(path_of_the_directory+"/"+files))
    else:
        continue

current_sample_no = 0

while bhb.update():

    if bhb.button.pressed:
        current_sample_no += 1
        if current_sample_no >= len(samples):
            current_sample_no = 0

    if bhb.gate_in.triggered:
        bhb.play(samples[current_sample_no], pitch_cv=bhb.pitch_in)
