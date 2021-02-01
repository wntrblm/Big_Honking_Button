"""This makes an arbitrary long honk with intro/loop/outro samples from a sliced up honk.wav
"""
import time
import winterbloom_bhb

bhb = winterbloom_bhb.BigHonkingButton()

sample_p1 = bhb.load_sample("samples/honk_p1.wav")
sample_p2 = bhb.load_sample("samples/honk_p2.wav") # edited in audacity, this part should be very small and loop well
sample_p3 = bhb.load_sample("samples/honk_p3.wav")

is_pressed = False # makes the second if statement only run once on button release

while True:
    if bhb.triggered:
        bhb.gate_out=True
        is_pressed = True
        bhb.play(sample_p1, pitch_cv=bhb.pitch_in)
        time.sleep(0.08) # the length of sample_p1
        bhb.play(sample_p2, pitch_cv=bhb.pitch_in, loop=True)

    if bhb.released and is_pressed:
        bhb.gate_out=False
        is_pressed = False
        bhb.play(sample_p3, pitch_cv=bhb.pitch_in)

