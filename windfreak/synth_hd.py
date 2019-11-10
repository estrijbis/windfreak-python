from .device import SerialDevice
from collections.abc import Sequence


class SynthHDChannel:

    def __init__(self, parent, index):
        self._parent = parent
        self._index = index

    def init(self):
        """Initialize device."""
        self.enable = False
        self.frequency = self.frequency_range['start']
        self.power = self.power_range['start']
        self.phase = 0.
        self.temp_compensation_mode = '10 sec'

    def write(self, attribute, *args):
        self.select()
        self._parent.write(attribute, *args)

    def read(self, attribute, *args):
        self.select()
        return self._parent.read(attribute, *args)

    def select(self):
        """Select channel."""
        self._parent.write('channel', self._index)

    @property
    def frequency_range(self):
        """Frequency range in Hz.

        Returns:
            dict: frequency range
        """
        return {
            'start': 53.e6,
            'stop': 13999.999999e6,
            'step': 0.1,
        }

    @property
    def frequency(self):
        """Get frequency in Hz.

        Returns:
            float: frequency in Hz
        """
        return self.read('frequency') * 1e6

    @frequency.setter
    def frequency(self, value):
        """Set frequency in Hz.

        Args:
            value (float / int): frequency in Hz
        """
        f_range = self.frequency_range
        if not isinstance(value, (float, int)) or not f_range['start'] <= value <= f_range['stop']:
            raise ValueError('Expected float in range [{}, {}] Hz.'.format(
                             f_range['start'], f_range['stop']))
        self.write('frequency', value / 1e6)

    @property
    def power_range(self):
        """Power range in dBm.

        Returns:
            dict: power range
        """
        return {
            'start': -60.,
            'stop': 20.,
            'step': 0.001,
        }

    @property
    def power(self):
        """Get power in dBm.

        Returns:
            float: power in dBm
        """
        return self.read('power')

    @power.setter
    def power(self, value):
        """Set power in dBm.

        Args:
            value (float / int): power in dBm
        """
        if not isinstance(value, (float, int)):
            raise TypeError('Expected float or int.')
        self.write('power', value)

    @property
    def calibrated(self):
        """Calibration was successful on frequency or amplitude change.

        Returns:
            bool: calibrated
        """
        return self.read('calibrated')

    @property
    def temp_compensation_modes(self):
        """Temperature compensation modes.

        Returns:
            tuple: tuple of str of modes
        """
        return ('none', 'on set', '1 sec', '10 sec')

    @property
    def temp_compensation_mode(self):
        """Temperature compensation mode.

        Returns:
            str: mode
        """
        return self.temp_compensation_modes[self.read('temp_comp_mode')]

    @temp_compensation_mode.setter
    def temp_compensation_mode(self, value):
        modes = self.temp_compensation_modes
        if not value in modes:
            raise ValueError('Expected str in set {}.'.format(modes))
        self.write('temp_comp_mode', modes.index(value))

    @property
    def vga_dac_range(self):
        """VGA DAC value range.

        Returns:
            dict: range
        """
        return {
            'start': 0,
            'stop': 45000,
            'step': 1,
        }

    @property
    def vga_dac(self):
        """Get raw VGA DAC value

        Returns:
            int: value
        """
        return self.read('vga_dac')

    @vga_dac.setter
    def vga_dac(self, value):
        """Set raw VGA DAC value.

        Args:
            value (int): value
        """
        if not isinstance(value, int):
            raise TypeError('Expected int.')
        self.write('vga_dac', value)

    @property
    def phase_range(self):
        """Phase step range.

        Returns:
            dict: range
        """
        return {
            'start': 0.,
            'stop': 360.,
            'step': .001,
        }

    @property
    def phase(self):
        """Get phase step value.

        Returns:
            float: value in degrees
        """
        return self.read('phase_step')

    @phase.setter
    def phase(self, value):
        """Set phase step value.

        Args:
            value (float / int): phase in degrees
        """
        if not isinstance(value, (float, int)):
            raise TypeError('Expected float or int.')
        self.write('phase_step', value)

    @property
    def rf_mute(self):
        """RF output mute.

        Returns:
            bool: mute
        """
        return not self.read('rf_mute')

    @rf_mute.setter
    def rf_mute(self, value):
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('rf_mute', not value)

    @property
    def pa_enable(self):
        """PA enable.

        Returns:
            bool: enable
        """
        return self.read('pa_power_on')

    @pa_enable.setter
    def pa_enable(self, value):
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('pa_power_on', value)

    @property
    def pll_enable(self):
        """PLL enable.

        Returns:
            bool: enable
        """
        return self.read('pll_power_on')

    @pll_enable.setter
    def pll_enable(self, value):
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('pll_power_on', value)

    @property
    def enable(self):
        """Get output enable.

        Returns:
            bool: enabled
        """
        return not self.rf_mute and self.pll_enable and self.pa_enable

    @enable.setter
    def enable(self, value):
        """Set output enable.

        Args:
            value (bool): enable
        """
        if not isinstance(value, bool):
            raise TypeError('Expected bool.')
        self.rf_mute = not value
        self.pll_enable = value
        self.pa_enable = value

    @property
    def lock_status(self):
        """PLL lock status.

        Returns:
            bool: locked
        """
        return self.read('pll_lock')


class SynthHD(SerialDevice, Sequence):

    API = {
        # name              type    write      read
        'channel':          (int,   'C{}',     'C?'),  # Select channel
        'frequency':        (float, 'f{:.7f}', 'f?'),  # Frequency in MHz
        'power':            (float, 'W{:.3f}', 'W?'),  # Power in dBm
        'calibrated':       (bool,  None,      'V'),
        'temp_comp_mode':   (int,   'Z{}',     'Z?'),
        'vga_dac':          (int,   'a{}',     'a?'),  # VGA DAC value [0, 45000]
        'phase_step':       (float, '~{:.3f}', '~?'),  # Phase step in degrees
        'rf_mute':          (bool,  'h{}',     'h?'),
        'pa_power_on':      (bool,  'r{}',     'r?'),
        'pll_power_on':     (bool,  'E{}',     'E?'),

        'model_type':       (str,   None,      '+'),
        'serial_number':    (int,   None,      '-'),
        'fw_version':       (str,   None,      'v0'),
        'hw_version':       (str,   None,      'v1'),
        'save':             (None,  'e',       None),
        'reference_mode':   (int,   'x{}',     'x?'),
        'trig_function':    (int,   'w{}',     'w?'),
        'pll_lock':         (bool,  None,      'p'),
        'temperature':      (float, None,      'z'),  # Temperature in Celsius
        'ref_frequency':    (float, '*{:.3f}', '*?'),  # Frequency in MHz

        'sweep_freq_low':   (int,   'l{}',     'l?'),
        'sweep_freq_high':  (int,   'u{}',     'u?'),
        'sweep_freq_step':  (int,   's{}',     's?'),
        'sweep_time_step':  (int,   't{:.3f}', 't?'),  # Time step in [4, 10000] ms
        'sweep_power_low':  (int,   '[{:.3f}', '[?'),  # Low power sweep [-60, +20] dBm
        'sweep_power_high': (int,   ']{:.3f}', ']?'),  # High power sweep [-60, +20] dBm
        'sweep_direction':  (int,   '^{}',     '^?'),
        'sweep_diff_freq':  (int,   'k{}',     'k?'),  # Differential frequency in MHz
        'sweep_diff_meth':  (int,   'n{}',     'n?'),  # Differential method
        'sweep_type':       (int,   'X{}',     'X?'),
        'sweep_single':     (bool,  'g{}',     'g?'),
        'sweep_cont':       (bool,  'c{}',     'c?'),

        'am_time_step':     (int,   'F{}',     'F?'),  # Time step in microseconds
        'am_num_samples':   (int,   'q{}',     'q?'),  # Number of samples in one burst
        'am_cont':          (bool,  'A{}',     'A?'),  # Enable continuous AM modulation
        'am_lookup_table':  (int,   '@{}{}',   '@{}?'),  # Program row in lookup table in dBm

        'pulse_on_time':    (int,   'P{}',     'P?'),  # Pulse on time in range [1, 10e6] us
        'pulse_off_time':   (int,   'O{}',     'O?'),  # Pulse off time in range [2, 10e6] uS
        'pulse_num_rep':    (int,   'R{}',     'R?'),  # Number of repetitions in range [1, 65500]
        'pulse_invert':     (bool,  ':{}',     ':?'),  # Invert pulse polarity
        'pulse_single':     (None,  'G',       None),
        'pulse_cont':       (bool,  'j{}',     'j?'),
        'dual_pulse_mod':   (bool,  'D{}',     'D?'),

        'fm_frequency':     (int,   '<{}',     '<?'),
        'fm_deviation':     (int,   '>{}',     '>?'),
        'fm_num_samples':   (int,   ',{}',     ',?'),
        'fm_mod_type':      (int,   ';{}',     ';?'),
        'fm_cont':          (bool,  '/{}',     '/?'),
    }

    def __init__(self, devpath):
        super().__init__(devpath)
        self._channels = [SynthHDChannel(self, index) for index in range(2)]

    def __getitem__(self, key):
        return self._channels.__getitem__(key)

    def __len__(self):
        return self._channels.__len__()

    def init(self):
        """Initialize device."""
        self.reference_mode = 'internal 27mhz'
        self.trigger_mode = 'disabled'
        self.sweep_enable = False
        self.am_enable = False
        self.pulse_mod_enable = False
        self.dual_pulse_mod_enable = False
        self.fm_enable = False
        for channel in self:
            channel.init()

    @property
    def model_type(self):
        """Model type.

        Returns:
            str: model
        """
        return self.read('model_type')

    @property
    def serial_number(self):
        """Serial number

        Returns:
            int: serial number
        """
        return self.read('serial_number')

    @property
    def firmware_version(self):
        """Firmware version.

        Returns:
            str: version
        """
        return self.read('fw_version')

    @property
    def hardware_version(self):
        """Hardware version.

        Returns:
            str: version
        """
        return self.read('hw_version')

    def save(self):
        """Save all settings to non-volatile EEPROM."""
        self.write('save')

    @property
    def reference_modes(self):
        """Frequency reference modes.

        Returns:
            tuple: tuple of str of modes
        """
        return ('external', 'internal 27mhz', 'internal 10mhz')

    @property
    def reference_mode(self):
        """Get frequency reference mode.

        Returns:
            str: mode
        """
        return self.reference_modes[self.read('reference_mode')]

    @reference_mode.setter
    def reference_mode(self, value):
        """Set frequency reference mode.

        Args:
            value (str): mode
        """
        modes = self.reference_modes
        if not value in modes:
            raise ValueError('Expected str in set {}.'.format(modes))
        self.write('reference_mode', modes.index(value))

    @property
    def trigger_modes(self):
        """Trigger modes.

        Returns:
            tuple: tuple of str of modes
        """
        return (
            'disabled',
            'full frequency sweep',
            'single frequency step',
            'stop all',
            'rf enable',
            'remove interrupts',
            'reserved',
            'reserved',
            'am modulation',
            'fm modulation',
        )

    @property
    def trigger_mode(self):
        """Get trigger mode.

        Returns:
            str: mode
        """
        return self.trigger_modes[self.read('trig_function')]

    @trigger_mode.setter
    def trigger_mode(self, value):
        """Set trigger mode.

        Args:
            value (str): mode
        """
        modes = self.trigger_modes
        if not value in modes:
            raise ValueError('Expected str in set {}.'.format(modes))
        self.write('trig_function', modes.index(value))

    @property
    def temperature(self):
        """Temperature in Celsius.

        Returns:
            float: temperature
        """
        return self.read('temperature')

    @property
    def reference_frequency_range(self):
        """Reference frequency range in Hz.

        Returns:
            dict: frequency range in Hz
        """
        return {
            'start': 10.e6,
            'stop': 100.e6,
            'step': 1.e3,
        }

    @property
    def reference_frequency(self):
        """Get reference frequency in Hz.

        Returns:
            float: frequency in Hz
        """
        return self.read('ref_frequency') * 1.e6

    @reference_frequency.setter
    def reference_frequency(self, value):
        """Set reference frequency in Hz.

        Args:
            value (float / int): frequency in Hz
        """
        f_range = self.reference_frequency_range
        if not isinstance(value, (float, int)) or not f_range['start'] <= value <= f_range['stop']:
            raise ValueError('Expected float in range [{}, {}] Hz.'.format(
                             f_range['start'], f_range['stop']))
        self.write('ref_frequency', value / 1.e6)

    @property
    def sweep_enable(self):
        """Get sweep continuously enable.

        Returns:
            bool: enable
        """
        return self.read('sweep_cont')

    @sweep_enable.setter
    def sweep_enable(self, value):
        """Set sweep continuously enable.

        Args:
            value (bool): enable
        """
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('sweep_cont', value)

    @property
    def am_enable(self):
        """Get AM continuously enable.

        Returns:
            bool: enable
        """
        return self.read('am_cont')

    @am_enable.setter
    def am_enable(self, value):
        """Set AM continuously enable.

        Args:
            value (bool): enable
        """
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('am_cont', value)

    @property
    def pulse_mod_enable(self):
        """Get pulse modulation continuously enable.

        Returns:
            bool: enable
        """
        return self.read('pulse_cont')

    @pulse_mod_enable.setter
    def pulse_mod_enable(self, value):
        """Set pulse modulation continuously enable.

        Args:
            value (bool): enable
        """
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('pulse_cont', value)

    @property
    def dual_pulse_mod_enable(self):
        """Get dual pulse modulation enable.

        Returns:
            bool: enable
        """
        return self.read('dual_pulse_mod')

    @dual_pulse_mod_enable.setter
    def dual_pulse_mod_enable(self, value):
        """Set dual pulse modulation enable.

        Args:
            value (bool): enable
        """
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('dual_pulse_mod', value)

    @property
    def fm_enable(self):
        """Get FM continuously enable.

        Returns:
            bool: enable
        """
        return self.read('fm_cont')

    @fm_enable.setter
    def fm_enable(self, value):
        """Set FM continuously enable.

        Args:
            value (bool): enable
        """
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')
        self.write('fm_cont', value)