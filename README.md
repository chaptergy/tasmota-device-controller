#  Tasmota Device Controller

This packag provides wrappers for Tasmota's web request API.

Only very few requests are implemented so far! If you need other requests, you can implement these commands and create a merge request on [GitHub](https://github.com/chaptergy/tasmota-device-controller), or create an issue.

Example usage:

```py
from tasmota_device_controller import TasmotaDevice
from tasmota_device_controller import tasmota_commands as cmd
from tasmota_device_controller import tasmota_types as t

device = TasmotaDevice('192.168.10.21')

# Set power of first output to on
setResult = device.sendRequest(
    cmd.Power(t.PowerType.ON, t.PowerOutputType.OUTPUT_1))
print(setResult)  # Returns {'POWER': 'ON'}

# Get current power state of second output
getResult = device.sendRequest(
    cmd.Power(powerOutput=t.PowerOutputType.OUTPUT_2))
print(getResult)  # Returns {'POWER': 'OFF'}

```