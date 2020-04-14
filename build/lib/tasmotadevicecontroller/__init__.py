from aiohttp import ClientSession, ClientTimeout
from typing import List

from . import tasmota_types as t


class TasmotaDevice():

    @classmethod
    async def connect(cls, url: str, username: str = None, password: str = None, timeout: int = 30):
        """Creates a TasmotaDevice instance. If a webUI password is set, both username and password are required. The username is usually 'admin'"""
        self = TasmotaDevice()

        self._timeout = ClientTimeout(total=int(timeout))

        if (username is None) != (password is None):
            raise ValueError(
                "Username and password must either be both not set or both set!")

        # Remove trailing slashes from url and add http if necessary
        self._url = url.rstrip('/')
        if not self._url.startswith('http://') and not self._url.startswith('https://'):
            self._url = 'http://' + self._url

        self._login_info = {'user': username,
                        'password': password} if password is not None else {}

        # Test provided configuration
        try:
            response = await self.getStatus()
            if response.get('Status') is None:
                if response.get('WARNING') == 'Need user=<username>&password=<password>':
                    if password is None: raise ConnectionError(f'Username (usually admin) and password are required')
                    else: raise ConnectionError(f'Username and / or password are invalid')
                else:
                    raise ConnectionError(response)
        except Exception as e:
            raise ConnectionError(f'Failed to connect to tasmota device: {str(e)}') from None

        return self

    async def sendRawRequest(self, command: str) -> dict:
        """Send an custom text command to the Tasmota device. The answer (JSON data) will be returned."""
        async with ClientSession(timeout=self._timeout) as session:
            params = {'cmnd': str(command), **self._login_info}
            # print('Sent command: ', params['cmnd'])
            async with session.get(f"{self._url}/cm", params=params) as resp:
                if resp.status != 200: raise Exception(f'Unexpected HTTP status {resp.status}: {resp.text()}')
                try:
                    return await resp.json()
                except:
                    raise Exception(f'Non-JSON data returned by device: {resp.text()}') from None


    #####################################################################
    ########################   Wrapper Methods   ########################
    #####################################################################

    ######   Control   ######

    async def getBlinkCount(self) -> int:
        """Get the blink count (number of power toggles)."""
        response = await self.sendRawRequest('BlinkCount')
        if response.get('BlinkCount') is None: raise Exception(f'Command failed: {response}')
        return response.get('BlinkCount')

    async def setBlinkCount(self, value: int) -> int:
        """Set the blink count (number of power toggles).

        0 = blink many times before restoring power state
        1..32000 = set number of blinks
        """
        value = int(value)

        if value < 0 or value > 32000:
            raise ValueError('Value must be between 0 and 32000')

        response = await self.sendRawRequest(f'BlinkCount {value}')
        if response.get('BlinkCount') != value: raise Exception(f'Command failed: {response}')
        return value


    async def getBlinkTime(self) -> int:
        """Get the blink time (duration of power toggles)."""
        response = await self.sendRawRequest('BlinkTime')
        if response.get('BlinkTime') is None: raise Exception(f'Command failed: {response}')
        return response.get('BlinkTime')

    async def setBlinkTime(self, value: int) -> int:
        """Set the blink time (duration of power toggles).

        2..3600 = set duration of blinks in 0.1s increments (10 = 1s)
        """
        value = int(value)

        if value < 2 or value > 3600:
            raise ValueError("Value must be between 2 and 3600")

        response = await self.sendRawRequest(f'BlinkTime {value}')
        if response.get('BlinkTime') != value: raise Exception(f'Command failed: {response}')
        return value


    async def getPower(self, output: t.PowerOutputType = t.PowerOutputType.OUTPUT_1) -> bool:
        """Get the current power state of the power outputs on the device"""
        if not t._isValidEnumValue(output, t.PowerOutputType):
            raise ValueError(f"Received invalid value for 'output'!")

        output = output.value

        response = await self.sendRawRequest(f'Power{output}')
        if response.get('POWER') != 'ON' and response.get('POWER') != 'OFF': raise Exception(f'Command failed: {response}')
        return response.get('POWER') == 'ON'

    async def setPower(self, value: t.PowerType, output: t.PowerOutputType = t.PowerOutputType.OUTPUT_1) -> bool:
        """Control the power state of the power outputs on the device (also restarts PulseTime).

        Available power types:
        PowerType.OFF = turn the output off
        PowerType.ON = turn the output on
        PowerType.TOGGLE = if output is ON switch to OFF and vice versa
        PowerType.BLINK = toggle power for BlinkCount times each BlinkTime duration (only when output is not `ALL_OUTPUTS`; function will always return True) (at the end of blink, power state is returned to pre-blink state; does not control the status LED)
        PowerType.BLINK_OFF = stop blink sequence and return power state to pre-blink state (only when output is not `ALL_OUTPUTS`; function will always return True)
        """

        # Validate input
        if not t._isValidEnumValue(value, t.PowerType):
            raise ValueError(f"Received invalid value for 'value'!")
        if not t._isValidEnumValue(output, t.PowerOutputType):
            raise ValueError(f"Received invalid value for 'output'!")
        if (value is t.PowerType.BLINK or value is t.PowerType.BLINK_OFF) and output is t.PowerOutputType.ALL_OUTPUTS:
            raise ValueError(
                f"Power type 'BLINK' and 'BLINK_OFF' can only be set for specific outputs, not all!")

        parsedValue = value.value
        output = output.value

        response = await self.sendRawRequest(f'Power{output} {parsedValue}')
        if response.get('POWER') is None: raise Exception(f'Command failed: {response}')
        if value is t.PowerType.OFF:
            if response.get('POWER') != 'OFF': raise Exception(f'Command failed: {response}')
            return False
        elif value is t.PowerType.ON:
            if response.get('POWER') != 'ON': raise Exception(f'Command failed: {response}')
            return True
        elif value is t.PowerType.TOGGLE:
            if response.get('POWER') != 'ON' and response.get('POWER') != 'OFF': raise Exception(f'Command failed: {response}')
            return response.get('POWER') == 'ON'
        elif value is t.PowerType.BLINK:
            if response.get('POWER') != 'Blink ON': raise Exception(f'Command failed: {response}')
            return True
        elif value is t.PowerType.BLINK_OFF:
            if response.get('POWER') != 'Blink OFF': raise Exception(f'Command failed: {response}')
            return True

    ######   Management   ######

    async def getFriendlyName(self, output: t.FriendlyNameOutputType = t.FriendlyNameOutputType.OUTPUT_1) -> str:
        """Get the friendly name of a power output."""
        if not t._isValidEnumValue(output, t.FriendlyNameOutputType):
            raise ValueError(f"Received invalid value for 'output'!")

        output = output.value

        response = await self.sendRawRequest(f'FriendlyName{output}')
        if response.get(f'FriendlyName{output}') is None: raise Exception(f'Command failed: {response}')
        return response.get(f'FriendlyName{output}')

    async def setFriendlyName(self, value: str, output: t.FriendlyNameOutputType = t.FriendlyNameOutputType.OUTPUT_1) -> str:
        """Set the friendly name of a power output.  
        
        Possible values:
        1 = Reset friendly name to firmware default
        <value> = set friendly name (32 char limit)
        """
        if not t._isValidEnumValue(output, t.FriendlyNameOutputType):
            raise ValueError(f"Received invalid value for 'output'!")

        value = str(value)
        output = output.value

        if len(value) > 32:
            raise ValueError("Name must be at most 32 characters long")

        response = await self.sendRawRequest(f'FriendlyName{output} {value}')
        if response.get(f'FriendlyName{output}') != value: raise Exception(f'Command failed: {response}')
        return value


    async def getStatus(self, statusType: t.StatusType = t.StatusType.ABBREVIATED) -> dict:
        """Command to get status information about the Tasmota device.

        Available status types:
        ABBREVIATED = show abbreviated status information
        ALL = show all status information
        DEVICE_PARAMETERS = show device parameters information
        FIRMWARE = show firmware information
        LOGGING_AND_TELEMETRY = show logging and telemetry information
        MEMORY = show memory information
        NETWORK = show network information
        MQTT = show MQTT information
        TIME = show time information
        CONNECTED_SENSOR = show connected sensor information
        POWER_THRESHOLDS = show power thresholds (only on modules with power monitoring)
        TELE_PERIOD = show information equal to TelePeriod state message
        STACK_DUMP = in case of crash to dump the call stack saved in RT memory
        """
        if not t._isValidEnumValue(statusType, t.StatusType):
            raise ValueError(f"Received invalid value for 'statusType'!")

        statusType = statusType.value

        response = await self.sendRawRequest(f'Status {statusType}')
        # If first key does not include substring "Status"
        if 'Status' not in next(iter(response)): raise Exception(f'Command failed: {response}')
        return response
    



