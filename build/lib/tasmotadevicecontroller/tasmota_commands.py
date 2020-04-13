from abc import ABC, abstractmethod
from typing import List, Union

from . import tasmota_types as t


class _Command(ABC):
    """This is the abstract command class. All commands should must inherit this class, and it should not be instanciated by itself."""

    def __init__(self):
        """This is the constructor, so validate all received values in here"""
        super().__init__()

    @abstractmethod
    def __str__(self):
        """This method will convert the class to a string, so it should return the command as it should be passed to Tasmota"""
        pass


#####################################################################
############################   Control   ############################
#####################################################################


class Backlog(_Command):
    """List of commands to be executed in sequence. Set commands parameter to `None` to get the current backlog."""

    def __init__(self, commands: Union[List[_Command], None] = None):
        self._commands = []

        # If is not None, set value, otherwise get value
        if commands is not None:
            if len(commands) > 30:
                raise ValueError("A maximum of 30 commands are allowed")

            for command in commands:
                if not isinstance(command, _Command):
                    raise ValueError("All elements must be command objects!")
                self._commands.append(str(command))

        super().__init__()

    def __str__(self):
        return f'Backlog {";".join(self._commands)}'


class BlinkCount(_Command):
    """Get or set the blink count (number of power toggles). Set value parameter to `None` to get the current value.

    0 = blink many times before restoring power state
    1..32000 = set number of blinks
    """

    def __init__(self, value: Union[int, None] = None):
        # If is not None, set value, otherwise get value
        if value is not None:
            self._value = int(value)

            if self._value < 0 or self._value > 32000:
                raise ValueError("Value must be between 0 and 32000")
        else:
            self._value = ''
        super().__init__()

    def __str__(self):
        return f'BlinkCount {self._value}'


class BlinkTime(_Command):
    """Get or set the blink time (duration of power toggles). Set value parameter to `None` to get the current value.

    2..3600 = set duration of blinks in 0.1s increments (10 = 1s)
    """

    def __init__(self, value: Union[int, None] = None):
        # If is not None, set value, otherwise get value
        if value is not None:
            self._value = int(value)

            if self._value < 2 or self._value > 3600:
                raise ValueError("Value must be between 2 and 3600")
        else:
            self._value = ''
        super().__init__()

    def __str__(self):
        return f'BlinkTime {self._value}'


class Power(_Command):
    """Control the power state of the power outputs on the device (also restarts PulseTime). Set powerType parameter to `None` to get the current value.

    Available power types:
    None = get current value
    PowerType.OFF / 0 = turn the output off
    PowerType.ON / 1 = turn the output on
    PowerType.TOGGLE / 2 = if output is ON switch to OFF and vice versa
    PowerType.BLINK / 3 = toggle power for BlinkCount times each BlinkTime duration (cannot be used with PowerOutputType.ALL_OUTPUTS) (at the end of blink, power state is returned to pre-blink state; does not control the status LED)
    PowerType.BLINK_OFF / 4 = stop blink sequence and return power state to pre-blink state (cannot be used with PowerOutputType.ALL_OUTPUTS)
    """

    def __init__(self, powerType: Union[t.PowerType, None] = None, output: t.PowerOutputType = t.PowerOutputType.ALL_OUTPUTS):
        # Validate input
        if not t._isValidEnumValue(output, t.PowerOutputType):
            raise ValueError(f"Received invalid value for 'output'!")

        self._output = output.value

        # If is not None, set value, otherwise get value
        if powerType is not None:
            # Validate input
            if not t._isValidEnumValue(powerType, t.PowerType):
                raise ValueError(f"Received invalid value for 'powerType'!")
            if (powerType is t.PowerType.BLINK or powerType is t.PowerType.BLINK_OFF) and output is t.PowerOutputType.ALL_OUTPUTS:
                raise ValueError(
                    f"Power type 'blink' and 'blink_off' can only be set for specific outputs, not all!")

            self._type = powerType.value
        else:
            self._type = ''

        super().__init__()

    def __str__(self):
        return f'Power{self._output} {self._type}'


#####################################################################
###########################   Management   ##########################
#####################################################################


class Delay(_Command):
    def __init__(self, delay: int):
        """Command to set delay between two backlog commands with 0.1 second increment (10 = 1s) (value between 2..3600)"""

        self._delay = int(delay)

        if self._delay < 2 or self._delay > 3600:
            raise ValueError("Delay must be between 2 and 3600")

        super().__init__()

    def __str__(self):
        return f'Delay {self._delay}'

class FriendlyName(_Command):
    def __init__(self, value: Union[str, None], output: t.FriendlyNameOutputType = t.FriendlyNameOutputType.OUTPUT_1):
        """Get or set the friendly name of a power output. Set value to `None` to get current name. For values other than `None`, output must be set to something other than `FriendlyNameOutputType.ALL_OUTPUTS`. 
        
        Possible values:
        1 = Reset friendly name to firmware default
        <value> = set friendly name (32 char limit)
        """

        # Validate input
        if not t._isValidEnumValue(output, t.FriendlyNameOutputType):
            raise ValueError(f"Received invalid value for 'output'!")

        self._output = output.value

        # If is not None, set value, otherwise get value
        if value is not None:
            if output is t.FriendlyNameOutputType.ALL_OUTPUTS:
                raise ValueError(f"Friendly name cannot be set for all outputs at the same time!")

            self._value = str(value)

            if len(self._value) > 32:
                raise ValueError("Name must be at most 32 characters long")
        else:
            self._value = ''

        super().__init__()

    def __str__(self):
        return f'FriendlyName{self._output} {self._value}'

class Status(_Command):
    def __init__(self, statusType: t.StatusType = t.StatusType.ABBREVIATED):
        """Command to get status information about the Tasmota device.

        Available status types:
        ABBREVIATED / '' = show abbreviated status information
        ALL / 0 = show all status information
        DEVICE_PARAMETERS / 1 = show device parameters information
        FIRMWARE / 2 = show firmware information
        LOGGING_AND_TELEMETRY / 3 = show logging and telemetry information
        MEMORY / 4 = show memory information
        NETWORK / 5 = show network information
        MQTT / 6 = show MQTT information
        TIME / 7 = show time information
        CONNECTED_SENSOR / 8 = show connected sensor information
        POWER_THRESHOLDS / 9 = show power thresholds (only on modules with power monitoring)
        TELE_PERIOD / 11 = show information equal to TelePeriod state message
        STACK_DUMP / 12 = in case of crash to dump the call stack saved in RT memory
        """

        self._type = statusType.value
        super().__init__()

    def __str__(self):
        return f'Status {self._type}'
