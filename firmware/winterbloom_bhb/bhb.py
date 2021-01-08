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

import time

import audiocore
import audioio
import board
import digitalio
import winterbloom_voltageio

try:
    import _bhb
except ImportError:
    raise EnvironmentError("This BHB library requires CircuitPython >= 6.0.0")


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


class BigHonkingButton:
    def __init__(self):
        self.board_revision = _detect_board_revision()
        self.pitch_settle_time = 0.001
        self._button = digitalio.DigitalInOut(board.BUTTON)
        self._button.switch_to_input(pull=digitalio.Pull.UP)
        self._gate_in = digitalio.DigitalInOut(board.GATE_IN)
        self._gate_in.switch_to_input()
        self._gate_out = digitalio.DigitalInOut(board.GATE_OUT)
        self._gate_out.switch_to_output()
        self._pitch_in = winterbloom_voltageio.VoltageIn(_AnalogIn())

        if self.board_revision >= 5:
            self._pitch_in.direct_calibration(
                {4068: -5.0, 3049: -2.5, 2025: 0, 1001: 2.5, 8: 5.0}
            )
        else:
            self._pitch_in.direct_calibration(
                {4068: -2.0, 3049: -1.0, 2025: 0, 1001: 1.0, 8: 2.0}
            )

        self.audio_out = audioio.AudioOut(board.HONK_OUT)

        self._last_gate_value = False
        self._last_button_value = False

    @property
    def button(self):
        return not self._button.value

    @property
    def gate_in(self):
        return not self._gate_in.value

    @property
    def pitch_in(self):
        time.sleep(self.pitch_settle_time)
        return self._pitch_in.voltage

    @property
    def gate_out(self):
        return self._gate_out.value

    @gate_out.setter
    def gate_out(self, value):
        self._gate_out.value = value

    @property
    def triggered(self):
        button_value = self.button
        gate_value = self.gate_in
        if (not self._last_button_value and button_value) or (
            not self._last_gate_value and gate_value
        ):
            result = True
        else:
            result = False

        self._last_button_value = button_value
        self._last_gate_value = gate_value

        return result

    @property
    def released(self):
        button_value = self.button
        gate_value = self.gate_in
        if not button_value and not gate_value:
            result = True
        else:
            result = False

        return result

    def load_sample(self, path):
        return audiocore.WaveFile(open(path, "rb"))

    def play(self, sample, pitch_cv=None, loop=False):
        if pitch_cv is not None:
            sample.sample_rate = int(44100 * pow(2, pitch_cv))
        self.audio_out.stop()
        self.audio_out.play(sample, loop=loop)

    def stop(self):
        self.audio_out.stop()
