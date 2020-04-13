from enum import Enum


class PowerType(Enum):
    OFF = '0'
    ON = '1'
    TOGGLE = '2'
    BLINK = '3'
    BLINK_OFF = '4'

class PowerOutputType(Enum):
    ALL_OUTPUTS = '0'
    OUTPUT_1 = '1'
    OUTPUT_2 = '2'
    OUTPUT_3 = '3'
    OUTPUT_4 = '4'
    OUTPUT_5 = '5'
    OUTPUT_6 = '6'
    OUTPUT_7 = '7'
    OUTPUT_8 = '8'

class FriendlyNameOutputType(Enum):
    OUTPUT_1 = '1'
    OUTPUT_2 = '2'
    OUTPUT_3 = '3'
    OUTPUT_4 = '4'
    OUTPUT_5 = '5'
    OUTPUT_6 = '6'
    OUTPUT_7 = '7'
    OUTPUT_8 = '8'

class StatusType(Enum):
    ABBREVIATED = ''
    ALL = '0'
    DEVICE_PARAMETERS = '1'
    FIRMWARE = '2'
    LOGGING_AND_TELEMETRY = '3'
    MEMORY = '4'
    NETWORK = '5'
    MQTT = '6'
    TIME = '7'
    CONNECTED_SENSOR = '8'
    POWER_THRESHOLDS = '9'
    TELE_PERIOD = '11'
    STACK_DUMP = '12'


def _isValidEnumValue(value: any, enum: Enum) -> bool:
    values = set(item.value for item in enum)
    return value.value in values
