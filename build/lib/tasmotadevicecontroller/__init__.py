import requests
from typing import List

from . import tasmota_commands as cmd
from . import tasmota_types as t


class TasmotaDevice():
    def __init__(self, url: str, username: str = None, password: str = None, timeout: int = 30):
        if (username is None) != (password is None):
            raise ValueError(
                "Username and password must either be both not set or both set!")

        # Remove trailing slashes from url and add http if necessary
        self._url = url.rstrip('/')
        if not self._url.startswith('http://') and not self._url.startswith('https://'):
            self._url = 'http://' + self._url

        self._logininfo = {'user': username,
                           'password': password} if password is not None else {}

        self._timeout = timeout

        # Test provided configuration
        try:
            self.sendRequest(cmd.Status(t.StatusType.ABBREVIATED))
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"{str(e)}. Please verify the URL '{self._url}'") from None
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {str(e)}.") from None

    def sendRequest(self, command: cmd._Command) -> dict:
        """Send a command to the Tasmota device. The answer (JSON data) will be returned."""
        if not isinstance(command, cmd._Command):
            raise TypeError(
                "Parameter must be a command object from tasmota_commands!")
        return self.sendRawRequest(str(command))

    def sendRawRequest(self, command: str) -> dict:
        """Send an custom text command to the Tasmota device. The answer (JSON data) will be returned."""
        params = {'cmnd': str(command), **self._logininfo}
        print('Sent command: ', params['cmnd'])
        response = requests.get(
            self._url + '/cm', params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()


    #####################################################################
    ########################   Wrapper Methods   ########################
    #####################################################################

    ######   Control   ######

    def getBacklog(self):
        """Get the current list of commands to be executed in sequence."""
        return self.sendRequest(cmd.Backlog(None))

    def setBacklog(self, commands: List[cmd._Command]):
        """Execute a list of commands in sequence."""
        return self.sendRequest(cmd.Backlog(commands))


    def getBlinkCount(self):
        """Get the blink count (number of power toggles)."""
        return self.sendRequest(cmd.BlinkCount(None))

    def setBlinkCount(self, value: int):
        """Set the blink count (number of power toggles).

        0 = blink many times before restoring power state
        1..32000 = set number of blinks
        """
        return self.sendRequest(cmd.BlinkCount(value))


    def getBlinkTime(self):
        """Get the blink time (duration of power toggles)."""
        return self.sendRequest(cmd.BlinkCount(None))

    def setBlinkTime(self, value: int):
        """Set the blink time (duration of power toggles).

        2..3600 = set duration of blinks in 0.1s increments (10 = 1s)
        """
        return self.sendRequest(cmd.BlinkCount(value))


    def getPower(self, powerOutput: t.PowerOutputType = t.PowerOutputType.ALL_OUTPUTS):
        """Get the current power state of the power outputs on the device"""
        return self.sendRequest(cmd.Power(None, powerOutput))

    def setPower(self, value: t.PowerType, powerOutput: t.PowerOutputType = t.PowerOutputType.ALL_OUTPUTS):
        """Control the power state of the power outputs on the device (also restarts PulseTime).

        Available power types:
        PowerOutputType.OFF / 0 = turn the output off
        PowerOutputType.ON / 1 = turn the output on
        PowerOutputType.TOGGLE / 2 = if output is ON switch to OFF and vice versa
        PowerOutputType.BLINK / 3 = toggle power for BlinkCount times each BlinkTime duration (at the end of blink, power state is returned to pre-blink state; does not control the status LED)
        PowerOutputType.BLINK_OFF / 4 = stop blink sequence and return power state to pre-blink state
        """
        return self.sendRequest(cmd.Power(value, powerOutput))

    ######   Management   ######

    def getFriendlyName(self, output: t.FriendlyNameOutputType = t.FriendlyNameOutputType.OUTPUT_1):
        """Get the friendly name of a power output.  
        """
        return self.sendRequest(cmd.FriendlyName(None, output))

    def setFriendlyName(self, value: str, output: t.FriendlyNameOutputType = t.FriendlyNameOutputType.OUTPUT_1):
        """Set the friendly name of a power output.  
        
        Possible values:
        1 = Reset friendly name to firmware default
        <value> = set friendly name (32 char limit)
        """
        return self.sendRequest(cmd.FriendlyName(value, output))


    def getStatus(self, statusType: t.StatusType = t.StatusType.ABBREVIATED):
        return self.sendRequest(cmd.Status(statusType))
    



