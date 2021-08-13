# The MIT License (MIT)
#
# Copyright (c) 2020 Alethea Flowers for Winterbloom
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import audiocore
import audioio
import board
import digitalio
import winterbloom_voltageio

try:
    import _bhb
except ImportError:
    raise RuntimeError("This BHB library requires CircuitPython >= 6.0.0")


def _detect_board_revision():
    v5pin = digitalio.DigitalInOut(board.V5)
    v5pin.switch_to_input(pull=digitalio.Pull.UP)

    # Pulled low on v5+, pull-up will make it true
    # on <=v4.
    if not v5pin.value:
        return 5
    else:
        return 4


class _AnalogIn:
    def __init__(self):
        _bhb.init_adc()

    @property
    def value(self):
        return _bhb.read_adc()


class _InputState:
    def __init__(self, pin):
        self._in = digitalio.DigitalInOut(pin)
        self._in.switch_to_input(pull=digitalio.Pull.UP)
        self.state = False
        self.last_state = False

    def update(self):
        self.last_state = self.state
        self.state = not self._in.value

    @property
    def rising_edge(self):
        return self.state and not self.last_state

    @property
    def falling_edge(self):
        return not self.state and self.last_state

    @property
    def value(self):
        return self.state

    pressed = rising_edge
    triggered = rising_edge
    released = falling_edge
    held = value
    __bool__ = value


class BigHonkingButton:
    def __init__(self):
        self.board_revision = _detect_board_revision()
        self._button = _InputState(board.BUTTON)
        self._gate_in = _InputState(board.GATE_IN)
        self._gate_out = digitalio.DigitalInOut(board.GATE_OUT)
        self._gate_out.switch_to_output()

        self._pitch_in = winterbloom_voltageio.VoltageIn(_AnalogIn())

        if self.board_revision >= 5:
            self._pitch_in.direct_calibration(
                {4068: -5.0, 3049: -2.5, 2025: 0, 1001: 2.5, 8: 5.0}
            )
            self.min_cv = -5.0
            self.max_cv = 5.0
        else:
            self._pitch_in.direct_calibration(
                {4068: -2.0, 3049: -1.0, 2025: 0, 1001: 1.0, 8: 2.0}
            )
            self.min_cv = -2.0
            self.max_cv = 2.0

        self.audio_out = audioio.AudioOut(board.HONK_OUT)

    def update(self):
        self._gate_in.update()
        self._button.update()
        return True

    @property
    def button(self):
        return self._button

    @property
    def gate_in(self):
        return self._gate_in

    @property
    def pitch_in(self):
        return self._pitch_in.voltage

    @property
    def gate_out(self):
        return self._gate_out.value

    @gate_out.setter
    def gate_out(self, value):
        self._gate_out.value = value

    @property
    def triggered(self):
        return self._button.triggered or self._gate_in.triggered

    @property
    def released(self):
        return self._button.released or self._gate_in.released

    def load_sample(self, path):
        return audiocore.WaveFile(open(path, "rb"))

    def play(self, sample, pitch_cv=None, loop=False):
        if pitch_cv is not None:
            sample_rate = min(int(44100 * pow(2, pitch_cv)), (350000 - 1))
            sample.sample_rate = sample_rate
        self.audio_out.stop()
        self.audio_out.play(sample, loop=loop)

    def stop(self):
        self.audio_out.stop()

    def select_from_list_using_cv(self, list, cv, low=None, high=None):
        if low is None:
            low = self.min_cv
        if high is None:
            high = self.max_cv

        cv = min(high, max(low, cv))
        count = len(list) - 1
        span = high - low
        value = cv - low
        index = int((value / span) * count)
        return list[index]
