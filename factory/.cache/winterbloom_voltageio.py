# The MIT License (MIT)
#
# Copyright (c) 2019 Alethea Flowers for Winterbloom
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

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/theacodes/Winterbloom_VoltageIO.git"

"""A helper library to setting a DACs to voltage values and reading voltage
values from ADCs.

That is, instead of setting a 16-bit integer value you can set the DAC to a
floating-point voltage value. See `VoltageOut` for more details. Same for
ADCs: instead of reading a 16-bit integer value you can read the voltage
value directly.
"""

import analogio


def _take_nearest_pair(values, target):
    """Given a sorted, monotonic list of values and a target value,
    returns the closest two pairs of numbers in the list
    to the given target. The first being the closest number
    less than the target, the second being the closest number
    greater than the target.

    For example::

        >>> _take_nearest_pair([1, 2, 3], 2.5)
        (2, 3)

    If the target is not part of the continuous range of the
    values, then both numbers will either be the minimum or
    maximum value in the list.

    For example::

        >>> _take_nearest_pair([1, 2, 3], 10)
        (3, 3)

    """
    low = values[0]
    high = values[0]

    for value in values:
        if value <= target and value >= low:
            low = value
        if value > target:
            high = value
            break
    else:
        # If we never found a value higher than
        # the target, the the target is outside
        # of the range of the list. Therefore,
        # the highest close number is also the
        # lowest close number.
        high = low

    return low, high


class VoltageOut:
    """Wraps an AnalogOut instance and allows you to set the voltage instead
    of specifying the 16-bit output value.

    Example::

        vout = winterbloom_voltageio.VoltageOut.from_pin(board.A1)
        vout.linear_calibration(3.3)
        vout.voltage = 1.23

    With multiple calibration points, this class can help counteract any
    non-linearity present in the DAC. See `direct_calibration` for more
    info.
    """

    def __init__(self, analog_out):
        self._analog_out = analog_out
        self._calibration = {}
        self._voltage = 0

    @classmethod
    def from_pin(cls, pin):
        return cls(analogio.AnalogOut(pin))

    def linear_calibration(self, min_voltage, max_voltage):
        """Determines intermediate calibration values using the given
        a minimum and maximum output voltage. This is the
        simplest way to calibrate the output. It assumes that the DAC
        and any output scaling op amps have an exactly linear response.

        Example::

            # Output range is 0v to 10.26v.
            vout.linear_calibration(0.0, 10.26)

        """
        self._calibration[min_voltage] = 0
        self._calibration[max_voltage] = 65535

        self._calibration_keys = sorted(self._calibration.keys())

    def direct_calibration(self, calibration):
        """Allows you to set the calibration values directly.

        A common case for this is to set the DAC's value to the point
        where it outputs 0%, 25%, 50%, 75%, and 100% of your output range
        and record the values at each point. You'd then pass the voltage
        and DAC values as the keys and values to this method.

        For example if your DAC outputs from 0v-3.3v your calibration might
        look something like this::

            vout.direct_calibration({
                0: 0,
                0.825: 16000,
                1.65: 32723,
                2.475: 49230,
                3.3, 65535,
            })

        You can keep adding more calibration points as needed to counteract
        any non-linearity in your DAC. You could even specify a calibration point
        for every output value of your DAC if your processor has enough RAM, though
        it's very likely overkill.
        """
        self._calibration.update(calibration)
        self._calibration_keys = sorted(self._calibration.keys())

    def _calibrated_value_for_voltage(self, voltage):
        if voltage in self._calibration:
            return self._calibration[voltage]

        low, high = _take_nearest_pair(self._calibration_keys, voltage)

        if high == low:
            normalized_offset = 0
        else:
            normalized_offset = (voltage - low) / (high - low)

        low_val = self._calibration[low]
        high_val = self._calibration[high]

        lerped = round(low_val + ((high_val - low_val) * normalized_offset))

        return min(lerped, 65535)

    def _get_voltage(self):
        return self._voltage

    def _set_voltage(self, voltage):
        self._voltage = voltage
        value = self._calibrated_value_for_voltage(voltage)
        self._analog_out.value = value

    voltage = property(_get_voltage, _set_voltage)


class VoltageIn:
    """Wraps an AnalogIn instance and allows you to read an ADC's measured voltage
    instead of the 16-bit input value.

    Example::

        vin = winterbloom_voltageio.VoltageIn.from_pin(board.A1)
        vin.linear_calibration(3.3)
        print(vin.voltage)

    With multiple calibration points, this class can help counteract any
    non-linearity present in the ADC. See `direct_calibration` for more
    info.
    """

    def __init__(self, analog_in):
        self._analog_in = analog_in
        self._calibration = {}

    @classmethod
    def from_pin(cls, pin):
        return cls(analogio.AnalogIn(pin))

    def linear_calibration(self, min_voltage, max_voltage):
        """Determines intermediate calibration values using the given
        a minimum and maximum output voltage. This is the
        simplest way to calibrate the input. It assumes that the ADC
        and any output scaling op amps have an exactly linear response.

        Example::

            # Input range is 0v to 10.26v.
            vin.linear_calibration(0, 10.26)

        """
        self._calibration[0] = 0
        self._calibration[65535] = max_voltage

        self._calibration_keys = sorted(self._calibration.keys())

    def direct_calibration(self, calibration):
        """Allows you to set the calibration values directly.

        A common case for this is to set known, stable input voltages
        into your ADC and record the measurement value. These values can
        be passed as the calibration data.

        For example if your ADC has a range of 0v to 4v and you measure
        the value at each integral voltage your calibration would look
        something like like this::

            vin.direct_calibration({
                0: 0,
                16000: 1.0,
                32723: 2.0,
                49230: 3.0,
                65535: 4.0,
            })
        """
        self._calibration.update(calibration)
        self._calibration_keys = sorted(self._calibration.keys())

    def _calibrated_voltage_for_value(self, value):
        if value in self._calibration:
            return self._calibration[value]

        low, high = _take_nearest_pair(self._calibration_keys, value)

        if high == low:
            normalized_offset = 0
        else:
            normalized_offset = (value - low) / (high - low)

        low_volt = self._calibration[low]
        high_volt = self._calibration[high]

        lerped = low_volt + ((high_volt - low_volt) * normalized_offset)

        return lerped

    def _get_voltage(self):
        return self._calibrated_voltage_for_value(self._analog_in.value)

    voltage = property(_get_voltage, None)
