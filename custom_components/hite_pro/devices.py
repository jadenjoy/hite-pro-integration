from contextlib import nullcontext
import rx

class DeviceState:
    def __init__(self, payload):
        self.raw = payload

    def __str__(self):
        return f"DeviceState({self.raw})"

class LightState(DeviceState):
    def __init__(self, switch, dimmvalue, payload):
        DeviceState.__init__(self, payload)
        self.switch = switch
        self.dimmvalue = dimmvalue

    def __str__(self):
        return f"LightState({self.switch}, {self.dimmvalue})"

    __repr__ = __str__


class BridgeDevice:
    def __init__(self, bridge, device_id, name):
        self.bridge = bridge
        self.device_id = device_id
        self.name = name

        self.state = rx.subject.BehaviorSubject(None)

    def handle_state(self, payload):
        self.state.on_next(DeviceState(payload))

class Light(BridgeDevice):
    def __init__(self, bridge, device_id, name, dimmable):
        BridgeDevice.__init__(self, bridge, device_id, name)

        self.dimmable = dimmable

    def interpret_dimmvalue_from_payload(self, switch, payload):
        if not self.dimmable:
            return 99

        if not switch:
            return self.state.value.dimmvalue if self.state.value is not None else 99

        return payload['dimmvalue']


    def handle_state(self, payload):
        switch = (payload['type'] == "switch")
        dimmvalue = self.interpret_dimmvalue_from_payload(switch, payload)

        self.state.on_next(LightState(switch, dimmvalue, payload))

    async def switch(self, switch: bool):
        await self.bridge.switch_device(self.device_id, {"switch": switch})

    async def dimm(self, value: int):
        value = max(0, min(99, value))
        await self.bridge.slide_device(self.device_id, {"dimmvalue": value})

    def __str__(self):
        return f"Light({self.device_id}, \"{self.name}\", dimmable: {self.dimmable}, state:{self.state.value})"

    __repr__ = __str__


