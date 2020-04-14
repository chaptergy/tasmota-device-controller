#  Tasmota Device Controller

This packag provides async wrappers for Tasmota's web request API.

Only very few requests are implemented so far! If you need other requests, please have a look at the section [Contributing](#contributing), or create an issue.

`get` methods return the value of the fetched item, `set` methods return the new set value (so what the `get` method would return after the set). However there are some exceptions like `BLINK` for `setPower()` which always returns `True`, but that should be mentioned in the methods description.

Since this package was created for a Home Assistant integration, you can check out [that integration](https://github.com/chaptergy/homeassistant-tasmota-switch) for other sample usage.

Example usage:

```py
import asyncio
from tasmotadevicecontroller import TasmotaDevice
from tasmotadevicecontroller import tasmota_types as t

async def main():
    device = await TasmotaDevice.connect('192.168.10.21')

    # Get friendly name (of first output, which is the default output)
    nameResult = await device.getFriendlyName()
    print(nameResult)  # Returns 'My Tasmota Plug'

    # Get power of first output
    getResult = await device.getPower()
    print(getResult)  # Returns True (on)

    # Set power of first output to on
    setResult = await device.setPower(t.PowerType.TOGGLE)
    print(setResult)  # Returns True or False (depending if the device was switched on or off)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

```

## Contributing
If you want to add new requests, can implement these commands and create a merge request on [GitHub](https://github.com/chaptergy/tasmota-device-controller).

Almost every command is implemented as one getter method and one setter method. Add your command if possible in the same way inside the `TasmotaDevice` class. Remember to add descriptions to each method. This description can usually be taken from the Tasmota wiki.  
Also, remember to always use `async` `await`!

If the command takes values from a specific set of values, create an `Enum` inside `tasmota_types.py` for it.