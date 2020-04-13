#  Tasmota Device Controller

This packag provides wrappers for Tasmota's web request API.

Only very few requests are implemented so far! If you need other requests, please have a look at the section [Contributing](#contributing), or create an issue.

Example usage:

```py
from tasmotadevicecontroller import TasmotaDevice
from tasmotadevicecontroller import tasmota_types as t

device = TasmotaDevice('192.168.1.20')

# Get friendly name (of first output, which is the default output)
getResult = device.getFriendlyName()
print(getResult)  # Returns {'FriendlyName1': 'My Tasmota Plug'}

# Set power of first output to on
setResult = device.setPower(t.PowerType.ON)
print(setResult)  # Returns {'POWER': 'ON'}

```

## Contributing
If you want to add new requests, can implement these commands and create a merge request on [GitHub](https://github.com/chaptergy/tasmota-device-controller).

For every request there should be one class inside `tasmota_commands.py` inheriting from the `_Command` class. Make sure to add a comment to the new class, describing the command. This description can usually be taken from the Tasmota wiki.  
If the command takes values from a specific set of values, create an `Enum` inside `tasmota_types.py` for it.  
You should now also add one or more methods to the `TasmotaDevice` wrapping these commands for ease of use.