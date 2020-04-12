import requests
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
        # print('Sent command: ', params['cmnd'])
        response = requests.get(
            self._url + '/cm', params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()
