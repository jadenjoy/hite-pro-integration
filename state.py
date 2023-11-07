class State:
    def __init__(self):
        self._observers = []
        self._switch = False

    def subscribe(self, callback):
        self._observers.append(callback)

    def notify_observers(self):
        for observer in self._observers:
            observer(self._switch)

    @property
    def switch(self):
        return self._switch

    @switch.setter
    def switch(self, value):
        if isinstance(value, bool):
            self._switch = value
            self.notify_observers()
        else:
            print("Неверное значение. Пожалуйста, используйте True или False.")
