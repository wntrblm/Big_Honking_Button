# This makes an arbitrary long honk with intro/loop/outro samples from a sliced up honk.wav

import time
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

sample_p1 = bhb.load_sample("samples/honk_p1.wav")
sample_p2 = bhb.load_sample("samples/honk_p2.wav") # this part should be very small and loop well
sample_p3 = bhb.load_sample("samples/honk_p3.wav")

while bhb.update():
    if bhb.triggered:
        bhb.gate_out=True # passes the button state to the output
        bhb.play(sample_p1, pitch_cv=bhb.pitch_in, loop=False)
        time.sleep(0.08) # the length of sample_p1
        bhb.play(sample_p2, pitch_cv=bhb.pitch_in, loop=True)

    if bhb.released:
        bhb.gate_out=False # passes the button state to the output
        bhb.play(sample_p3, pitch_cv=bhb.pitch_in, loop=False)
