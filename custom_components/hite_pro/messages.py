from enum import IntEnum

class Messages(IntEnum):
    NACK = 0
    ACK = 1
    HEARTBEAT = 2
    SET_DEVICE_STATE = 3
    ACTION_SWITCH_DEVICE = 4


class SwitchState(IntEnum):
    ON = 1
    OFF = 2
    IMPULSE = 3