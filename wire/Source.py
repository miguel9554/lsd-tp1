from abc import ABC, abstractmethod


class Source(ABC):
    @abstractmethod
    def get_spiceopus_definition(self):
        raise NotImplementedError()


class StepSource(Source):

    def __init__(self, pulsed_value, pulse_width, period, initial_value=0, delay_time=0, rise_time=0, fall_time=0):
        self.initial_value = initial_value
        self.pulsed_value = pulsed_value
        self.delay_time = delay_time
        self.rise_time = rise_time
        self.fall_time = fall_time
        self.pulse_width = pulse_width
        self.period = period

    def get_spiceopus_definition(self):
        return 'vp 1 0 PULSE {initial_value} {pulsed_value} {delay_time} {rise_time} {fall_time} {pulse_width} {period}\n'.\
            format(initial_value=self.initial_value, pulsed_value=self.pulsed_value, delay_time=self.delay_time, rise_time=self.rise_time,
                   fall_time=self.fall_time, pulse_width=self.pulse_width, period=self.period)

