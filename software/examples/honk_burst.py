# This example turns the Big Honking Button into a simple
# burst generator (that also happens to honk)

import time

import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()
sample = bhb.load_sample("samples/honk.wav")
burst_intervals = [0.05, 0.05, 0.05, 0.05, 0.1]

while bhb.update():
    if bhb.triggered:
        for interval in burst_intervals:
            bhb.gate_out = True
            bhb.play(sample, pitch_cv=bhb.pitch_in)
            time.sleep(interval)
            bhb.gate_out = False
            bhb.stop()
            time.sleep(interval)
